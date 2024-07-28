from fasthtml.common import *
import redis
from tinyredis import TinyRedis

xtra_css = Style(':root { --pico-font-size: 100%; }')
app = FastHTML(secret_key=os.getenv('SESSKEY', 's3kret'),
               hdrs=[picolink, xtra_css, SortableJS('.sortable')])
rt = app.route

@dataclass
class Todo: id:str=None; title:str=''; done:bool=False; priority:int=0
todos = TinyRedis(redis.from_url(os.environ['VERCEL_KV_URL']), Todo)
def tid(id): return f'todo-{id}'

@patch
def __ft__(self:Todo):
    show = AX(self.title, f'/todos/{self.id}', 'current-todo')
    edit = AX('edit',     f'/edit/{self.id}' , 'current-todo')
    dt = ' ✅' if self.done else ''
    cts = (dt, show, ' | ', edit, Hidden(id="id", value=self.id), Hidden(id="priority", value="0"))
    return Li(*cts, id=f'todo-{self.id}')

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)

@rt("/")
async def get():
    add = Form(Group(mk_input(), Button("Add")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    items = sorted(todos(), key=lambda o: o.priority)
    frm = Form(*items, id='todo-list', cls='sortable', hx_post="/reorder", hx_trigger="end")
    return Titled('Todo list', Card(Ul(frm), header=add, footer=Div(id='current-todo')))

@rt("/reorder")
def post(id:list[str]):
    items = todos()
    pos = {u:i for i,u in enumerate(id)}
    for o in items: o.priority=pos[o.id]
    todos.insert_all(items)
    return tuple(sorted(items, key=lambda o: o.priority))

@rt("/todos/{id}")
async def delete(id:str):
    todos.delete(id)
    return clear('current-todo')

@rt("/")
async def post(todo:Todo): return todos.insert(todo), mk_input(hx_swap_oob='true')

@rt("/edit/{id}")
async def get(id:str):
    res = Form(Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), Checkbox(id="done", label='Done'),
        hx_put="/", target_id=tid(id), id="edit")
    return fill_form(res, todos[id])

@rt("/")
async def put(todo: Todo): return todos.update(todo), clear('current-todo')

@rt("/todos/{id}")
async def get(id:str):
    todo = todos[id]
    btn = Button('delete', hx_delete=f'/todos/{todo.id}',
                 target_id=tid(todo.id), hx_swap="outerHTML")
    return Div(Div(todo.title), btn)

serve()
