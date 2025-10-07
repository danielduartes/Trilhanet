from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError

# Função que permite que uma sessão seja criada e fechada 
def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally: # faz com que a sessão seja fechada independente do que aconteça
        session.close()


# Função para validar o token
def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)): 
    try:     
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM) # decodificando o token utilizando a SECRET_KEY e o ALGORITHM
        id_user = int(dic_info.get('sub')) # ID do usuário que foi pego no dicionário de informações
    except JWTError: 
        raise HTTPException(status_code=401, detail='Acesso negado, verifique a validade do token') # erro de token inválido
    user = session.query(Usuario).filter(Usuario.id_user==id_user).first() # procurando o ID no banco
    if not user:
        raise HTTPException(status_code=401, detail='Acesso inválido') # erro de nome de usuário incorreto
    return user