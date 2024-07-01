import redis, uuid
from json import loads,dumps
from dataclasses import dataclass,asdict

class TinyRedis:
    def __init__(self, r, typ, xtra={}): self.r,self.typ,self.nm,self.xtra = r,typ,typ.__name__,xtra

    def to_id(self, id):
        assert id
        return f'{self.nm}:{id}'

    def _xpand(self, d, o, kw):
        if d is None: d={}
        d = {**d, **kw}
        if o: d = {**asdict(o), **d}
        return {**d, **self.xtra}

    def insert(self, o=None, d=None, **kw):
        d = self._xpand(d, o, kw)
        if d.get('id',None) is None: d['id'] = str(uuid.uuid4())
        print(d.get('id',None))
        self.r.set(self.to_id(d['id']), dumps(d))
        return self.typ(**d)
    
    def update(self, o=None, d=None, **kw):
        d = self._xpand(d, o, kw)
        d = {**self.get(d['id']), **d}
        self.r.set(self.to_id(d['id']), dumps(d))
        return self.typ(**d)
    
    def delete(self, id): self.r.delete(self.to_id(id))
    
    def to_obj(self, j): return self.typ(**loads(j))
    def get(self, k): return loads(self.r.get(self.to_id(k)))
    def __getitem__(self, k): return self.typ(**self.get(k))
    
    def __call__(self):
        keys = self.r.scan_iter(match=f'{self.nm}:*', count=10000)
        return [self.to_obj(o) for o in self.r.mget(keys)]
