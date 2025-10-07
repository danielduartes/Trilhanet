from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PostSchema
from models import Postagem, Usuario, PostUpdate, LikePost, DislikePost

order_router = APIRouter(prefix='/order', tags=['pedidos'], dependencies=[Depends(verificar_token )]) # criando o roteador de pedidos

@order_router.get('/') # criando rota de GET (READ)
async def pedidos(): # função assíncrona
    return {'mensagem': 'Você acessou o meu site'} # mensagem a ser retornada

# Função para criar postagem
@order_router.post('/postar')
async def criar_postagem(post_schema: PostSchema, session: Session =  Depends(pegar_sessao)):
    new_post = Postagem(id_user=post_schema.id_user, username=post_schema.username, text=post_schema.text) # parâmetros da postagem (ID do usuário, nome do usuário e texto a ser publicado)
    session.add(new_post) # adicionando a postagem ao banco de dados
    session.commit() # commitando a mudança
    return {'mensagem': 'Postagem publicada com sucesso!'}



# Rota para listar todas as postagens
@order_router.get('/listar_posts')
async def listar_posts(session: Session = Depends(pegar_sessao), user: Usuario = Depends(verificar_token)):
    posts = session.query(Postagem).all()
    return {
        'posts': posts
    }


# Rota para listar todas as postagens do usuário cadastrado
@order_router.get('/listar_posts_user/')
async def listar_posts_usuario(session: Session = Depends(pegar_sessao), user: Usuario = Depends(verificar_token)):
    if not user:
        raise HTTPException(status_code=401, detail='Usuário não encontrado')
    posts = session.query(Postagem).filter(Postagem.username==user.username).all()
    if not posts:
        return {
            'mensagem': 'O usuário não fez nenhuma postagem'
        }
    return {
        'user': user,
        'posts': posts
    }


# Rota para editar um post
@order_router.put('/editar_post/{id_post}')
async def editar_post(id_post: int, post_data: PostUpdate, session: Session = Depends(pegar_sessao), user: Usuario = Depends(verificar_token)): # parâmetros: ID do post, sessão e token do usuário que logou
    post = session.query(Postagem).filter(Postagem.id_post==id_post).first() # pegando o post do ID digitado
    if not post:
        raise HTTPException(status_code=400, detail='Post não encontrado') # ID não existe
    post.text = post_data.text # editando o texto 
    if user.id_user != post.id_user: # caso o ID do usuário logado seja diferente do ID do usuário dono do post
        raise HTTPException(status_code=401, detail='Você não tem autorização para fazer essa modificação') 
    session.commit() # commitando a mudança feita no banco
    session.refresh(post) 
    return {
        'mensagem': f'Post número: {post.id_post} editado com sucesso', # mensagem na API
        'post': post
    }


# Rota para deletar um post
@order_router.delete('/deletar_post/{id_post}')
async def deletar_post(id_post: int, session: Session = Depends(pegar_sessao), user: Usuario = Depends(verificar_token)):
    post = session.query(Postagem).filter(Postagem.id_post==id_post).first()
    if not post:
        raise HTTPException(status_code=400, detail='Post não encontrado')
    if user.id_user != post.id_user:
        raise HTTPException(status_code=401, detail='Você não tem autorização para fazer essa modificação')
    session.delete(post)
    session.commit()
    return {
        'mensagem': f'Post de ID: {id_post} deletado com sucesso!'
    }


# Rota para dar like em um post
@order_router.post('/like_post/{id_post}')
async def like_post(id_post: int, session: Session = Depends(pegar_sessao), user: Usuario = Depends(verificar_token)):
    already_disliked = session.query(DislikePost).filter(DislikePost.id_post==id_post, DislikePost.id_user==user.id_user).first() # verificando se o usuário já deu dislike 
    if already_disliked: # se sim retira o dislike (só é permitido uma interação por usuário)
        session.delete(already_disliked) # tirando o usuário na tabela de quem deu dislike no post
        session.query(Postagem).filter(Postagem.id_post==id_post).update({Postagem.dislikes: Postagem.dislikes - 1}, synchronize_session=False) # diminuindo uma unidade na coluna de dislikes do post
    already_liked = session.query(LikePost).filter(LikePost.id_post==id_post, LikePost.id_user==user.id_user).first() # verificando se o usuário já deu like na postagem
    if already_liked: # se sim retira o like
        session.delete(already_liked) # tirando o usuário na tabela de quem deu like post
        session.query(Postagem).filter(Postagem.id_post==id_post).update({Postagem.likes: Postagem.likes - 1}, synchronize_session=False) # diminuindo uma unidade na coluna dos likes
        session.commit() # commitando a mudança no banco
        return {'mensagem': 'Post descurtido com sucesso!'}
    else:
        like = LikePost(id_post=id_post, id_user=user.id_user) # dando like no post
        session.add(like) # adicionando o like

        try:
            session.commit() # commitando a mudança
            session.query(Postagem).filter(Postagem.id_post==id_post).update({Postagem.likes: Postagem.likes + 1}, synchronize_session=False) # adicionando uma unidade na coluna de likes
            session.commit() # commitando a mudança
            return {'mensagem': 'Post curtido com sucesso!'}
        except Exception as e: 
            session.rollback() # revertendo as mudanças no banco caso ocorra algum erro
            raise HTTPException(status_code=409, detail=str(e))



# Rota de dislike em um post
@order_router.post('/dislike_post/{id_post}')
async def like_post(id_post: int, session: Session = Depends(pegar_sessao), user: Usuario = Depends(verificar_token)):
    already_liked = session.query(LikePost).filter(LikePost.id_post==id_post, LikePost.id_user==user.id_user).first() # verificando se o usuário já deu like no post
    if already_liked: # se sim retira o like (só é permitido uma interação por usuário)
        session.delete(already_liked) # deletando o usuário na tabela de quem deu like no post
        session.query(Postagem).filter(Postagem.id_post==id_post).update({Postagem.likes: Postagem.likes - 1}, synchronize_session=False) # diminuindo uma unidade na coluna de likes do post
    already_disliked = session.query(LikePost).filter(LikePost.id_post==id_post, LikePost.id_user==user.id_user).first() # verificando se o usuário já deu dislike no post
    if already_disliked: # se sim retira o dislike
        session.delete(already_disliked) # tirando o usuário da tabela de quem deu dislike no post
        session.query(Postagem).filter(Postagem.id_post==id_post).update({Postagem.dislikes: Postagem.dislikes - 1}, synchronize_session=False) # diminuindo uma unidade na coluna de dislikes do post
        session.commit() # commitando a mudança
        return {'mensagem': 'Dislike desfeito com sucesso!'}
    else:
        dislike = LikePost(id_post=id_post, id_user=user.id_user) # dando dislike no post
        session.add(dislike) # adicionando o dislike

        try:
            session.commit() # commitando a mudanla
            session.query(Postagem).filter(Postagem.id_post==id_post).update({Postagem.dislikes: Postagem.dislikes + 1}, synchronize_session=False) # adicionando uma unidade na coluna de dislikes do post
            session.commit() # commitando a mudança
            return {'mensagem': 'Dislike feito com sucesso!'}
        except Exception as e:
            session.rollback() # desfazendo as mudanças no banco caso ocorra algum erro
            raise HTTPException(status_code=409, detail=str(e))


