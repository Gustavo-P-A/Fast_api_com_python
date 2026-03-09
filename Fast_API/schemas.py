from pydantic import BaseModel
from typing import Optional, List

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool] = None
    adm: Optional[bool] = None

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    id_usuario: int

    class Config:
        from_attributes = True 

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco: float    

    class Config:
        from_attributes = True

class ResponsePedidoSchema(BaseModel):
    id: int
    preco: float
    status: str
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True