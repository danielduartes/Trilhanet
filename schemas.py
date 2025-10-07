from pydantic import BaseModel
from typing import Optional

# Esse arquivo foi criado para padronizar os dados tanto do cadastro de usuários quanto dos de uma postagem

# criando a base dos dados que devem ser preenchidos na hora de cadastrar um usuário
class UsuarioSchema(BaseModel):
    username: str
    email: str
    password: str
    activity: Optional[bool]

    class Config:
        from_attributes = True

# criando a base de dados que devem ser preenchidos na hora de criar um post
class PostSchema(BaseModel):
    id_user: int
    username: str
    text: str

    class Config:
        from_attributes = True


# criando a base de dados que devem ser preenchidos na hora de logar
class LoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True