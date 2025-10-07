from fastapi import APIRouter, Depends, HTTPException
from models import Usuario, db
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix = '/auth', tags=['autenticação']) # criando o roteador autenticação

# Função para criar o token (Autenticação JWT)
def creating_token(id_user):
    expiration_date = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # data de expiração do token
    # expiration_date = datetime.now(timezone.utc) + timedelta      # a data de expiração é um 'timedelta' por ser baseado em dais e não em minutos/horas
    dic_info = {'sub': str(id_user), 'expiration_date': expiration_date.isoformat()} # dicionário de informações (ID do usuário que está logando e a o horário de expiração do token)
    codeficated_jwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)  # codificando o token, parâmetros: dicionário de informações, chave secreta, algoritmo de codificação
    return codeficated_jwt # retorna o token codificado


# Função para checar se a senha digitada condiz com a senha descriptografada do usuário
def user_authentication(username, password, session):
    user = session.query(Usuario).filter(Usuario.username==username).first() # pegando todos os usuários no banco
    if not user: # nome de usuário incorreto
        return False 
    elif not bcrypt_context.verify(password, user.password): # senha incorreta
        return False
    return user # senha e usuário corretos

@auth_router.get('/') # criando rota de GET (READ)
async def home(): # função assíncrona
    return {'mensagem': 'Você acessou a rota padrão de autenticação', # mensagem a ser retornada
             'autenticação': True
             }



# Rota para criar uma conta (CREATE)
@auth_router.post('/criar_conta')
async def criar_conta(schema_user:UsuarioSchema, session: Session = Depends(pegar_sessao)):
    user =  session.query(Usuario).filter(Usuario.username==schema_user.username).first() # verificando no banco se existe um usuário igual ao que está sendo cadastrado
    if user:
        # Já existe um usuário com esse nome
        raise HTTPException(status_code=400, detail='Já existe um usuário com esse nome')
    else:
        # Não existe um usuário com esse nome
        exist_email = session.query(Usuario).filter(Usuario.email==schema_user.email).first() # verificando no banco se existe um email igual ao que está sendo cadastrado
        if exist_email:
            # Email já cadastrado
            raise HTTPException(status_code=400, detail='E-mail já cadastrado')
        else:
            # Email não cadastrado
            encrypted_password = bcrypt_context.hash(schema_user.password) # criptografando a senha
            new_user = Usuario(schema_user.username, schema_user.email, encrypted_password, schema_user.activity) # dados do novo usuário
            session.add(new_user) # adicionando o usuário
            session.commit() # commitando a mudança no banco de dados
            return {'mensagem': f"Usuário cadastrado com sucesso!"}
        

# Rota de login
@auth_router.post('/login')
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    user = user_authentication(login_schema.username, login_schema.password, session) # parâmetros da função de autenticação (nome de usuário e senha) 
    if not user: # usuário ou senha incorretos 
        raise HTTPException(status_code=400, detail='Usuário não encontrado ou credenciais inválidas')
    else:
        access_token = creating_token(user.id_user) # token retornado da função "creating_token"
        # refresh_token = creating_token(user.id_user, expiration_date=timedelta(days=7))     # definindo quanto tampo vai durar o refresh token (7 dias)
        return {
            'access_token': access_token,
            # 'refresh_token': refresh_token,    # retornando o refresh token 
            'token_type': 'Bearer'
        }
    

@auth_router.post('/login-form')
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    user = user_authentication(dados_formulario.username, dados_formulario.password, session) # parâmetros da função de login autenticado (nome de usuário e senha que foram preenchidos no formulário) 
    if not user: # usuário ou senha incorretos 
        raise HTTPException(status_code=400, detail='Usuário não encontrado ou credenciais inválidas')
    else:
        access_token = creating_token(user.id_user) # token retornado da função "creating_token"
        # refresh_token = creating_token(user.id_user, expiration_date=timedelta(days=7))     # definindo quanto tampo vai durar o refresh token (7 dias)
        return {
            'access_token': access_token,
            # 'refresh_token': refresh_token,    # retornando o refresh token 
            'token_type': 'Bearer'
        }


# Função para usar o token
@auth_router.get('/refresh')
async def use_refresh_token(user: Usuario = Depends(verificar_token)): # o parâmetro deve ser um token válido
    access_token = creating_token(user.id_user)
    return {
            'access_token': access_token,
            # 'refresh_token': refresh_token,    # caso eu utilizasse refresh token 
            'token_type': 'Bearer'
        }  