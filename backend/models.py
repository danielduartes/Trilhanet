from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint, func
from sqlalchemy.orm import declarative_base, relationship

# criando conexão com o banco
db = create_engine('sqlite:///banco.db')

# criando a base do banco de dados
Base = declarative_base()

# criando as classes/tabelas do banco

# Tabela dos usuários
class Usuario(Base):
    __tablename__ = 'Usuarios' # nome da tabela

    # Colunas da tabela
    id_user = Column('id_user', Integer, nullable=False, primary_key=True, autoincrement=True) # parâmetros: (nome da coluna, tipo de dado, campo não pode ser nulo, chave primária, campo vai ser preenchido sozinho se incrementando 1)
    username = Column('username', String, nullable=False, unique=True) # parâmetros: (nome da coluna, tipo de dado, campo não pode ser nulo)
    email = Column('email', String, nullable=False) # parâmetros: (nome da coluna, tipo de dado, campo não pode ser nulo)
    password = Column('password', String, nullable=False) # parâmetros: (nome da coluna, tipo de dado, campo não pode ser nulo)
    activity = Column('activity', Boolean, nullable=False, server_default='1', default=True)

    # Função de inicialização
    def __init__(self, username, email, password, activity=True): # parâmetros que serão obrigatórios na hora da criação do usuário pelo código em python
        self.username = username
        self.email = email
        self.password = password
        self.activity = activity


# Tabela das postagens
class Postagem(Base): 
    __tablename__ = 'Postagens'

    # Colunas da tabela
    id_post = Column('id_post', Integer, nullable=False, primary_key=True, autoincrement=True) 
    id_user = Column('id_user', Integer, ForeignKey('Usuarios.id_user'), nullable=False) # chave estrangeira para pegar o id do usuário na tabela dos usuários
    username = Column('user', String, ForeignKey('Usuarios.username'), nullable=False) # chave estrangeora para pegar o nome de usuário de quem fez a postagem na tabela dos usuários
    text = Column('text', String, nullable=False)
    date_time = Column('date_time', DateTime, server_default=func.now())
    likes = Column('likes', Integer, nullable=True, default=0)
    dislikes = Column('dislikes', Integer, nullable=True, default=0)

    usuario_por_id = relationship('Usuario', foreign_keys=[id_user])  # relacionamento pelo id_user
    usuario_por_nome = relationship('Usuario', foreign_keys=[username])   # relacionamento pelo user (username)

    model_config = ConfigDict(from_attributes=True)
 
    def __init__(self, id_user, username, text, date_time=None): # parâmetros que serão obrigatórios na hora da criação do usuário pelo código em python
        self.id_user = id_user
        self.username = username
        self.text = text
        if date_time:
            self.date_time = date_time


class PostUpdate(BaseModel):
    text: str


class LikePost(Base):
    __tablename__ = 'Like_Posts'

    # Colunas da tabela
    id_post = Column(Integer, ForeignKey('Postagens.id_post'), nullable=False, primary_key=True)
    id_user = Column(Integer, ForeignKey('Usuarios.id_user'), nullable=False, primary_key=True)

    __table_args__ = (
        UniqueConstraint('id_post', 'id_user', name='_user_post_uc'),
    )

    user = relationship('Usuario', foreign_keys=[id_user])
    post = relationship('Postagem', foreign_keys=[id_post])

    def __repr__(self):
        return f'<LikePost(id_post={self.id_post}, id_user={self.id_user})>'


class DislikePost(Base):
    __tablename__ = 'Dislike_Posts'

    # Colunas da tabela
    id_post = Column(Integer, ForeignKey('Postagens.id_post'), nullable=False, primary_key=True)
    id_user = Column(Integer, ForeignKey('Usuarios.id_user'), nullable=False, primary_key=True)

    __table_args__ = (
        UniqueConstraint('id_post', 'id_user', name='_user_post_uc'),
    )

    user = relationship('Usuario', foreign_keys=[id_user])
    post = relationship('Postagem', foreign_keys=[id_post])

    def __repr__(self):
        return f'<LikePost(id_post={self.id_post}, id_user={self.id_user})>'