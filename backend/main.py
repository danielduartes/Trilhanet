from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY') # chave para descriptografar as senhas
ALGORITHM = os.getenv('ALGORITHM') # algoritmo de codificação do token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')) # tempo de expiração do token (30 minutos)

app = FastAPI() # criando o objeto da API

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # criptografando as senhas
oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/login-form') # login autenticado

from auth_routes import auth_router # importando o roteador de autenticação
from order_routes import order_router # importando o roteador de criação, leitura, atualização e deleta de dados

app.include_router(auth_router) # incluindo o roteador de autenticação
app.include_router(order_router) # incluindo o roteador de pedidos