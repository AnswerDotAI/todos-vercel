from fasthtml.common import *
import redis
from tinyredis import TinyRedis

xtra_css = Style(':root { --pico-font-size: 100%; }')
app = FastHTML(secret_key=os.getenv('SESSKEY', 's3kret'),
               hdrs=[picolink, xtra_css])
rt = app.route

@dataclass
class Todo: id:str=None; title:str=''; done:bool=False
todos = TinyRedis(redis.from_url(os.environ['VERCEL_KV_URL']), Todo)
def tid(id): return f'todo-{id}'

@patch
def __xt__(self:Todo):
    show = AX(self.title, f'/todos/{self.id}', 'current-todo')
    edit = AX('edit',     f'/edit/{self.id}' , 'current-todo')
    dt = ' ✅' if self.done else ''
    return Li(show, dt, ' | ', edit, id=tid(self.id))

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)

@rt("/")
async def get():
    add = Form(Group(mk_input(), Button("Add")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    card = Card(Ul(*todos(), id='todo-list'),
                header=add, footer=Div(id='current-todo')),
    title = 'Todo list'
    return Title(title), Main(H1(title), card, cls='container')

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

run_uv()
