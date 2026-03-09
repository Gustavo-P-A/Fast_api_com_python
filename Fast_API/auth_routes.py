from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from core.settings import settings
from core.security import bcrypt_context
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm                                                                                                                                                                  

auth_router = APIRouter(prefix='/auth', tags=['auth'])


def criar_token(id_usuario, duracao_token=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    if isinstance(duracao_token, int):
        delta = timedelta(minutes=duracao_token)
    else:
        delta = duracao_token
        
    data_expiracao = datetime.now(timezone.utc) + delta 
    dic_info = {'sub': str(id_usuario), 'exp': data_expiracao}
    jwt_codificado = jwt.encode(dic_info, settings.SECRET_KEY, settings.ALGORITHM)
    return jwt_codificado


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    if not bcrypt_context.verify(senha, usuario.senha):
        return False    
    return usuario


@auth_router.get('/')
async def home():
    return{'mensagem': 'voce acesso a rota de autenticacao'}

@auth_router.post('/criar_usuario')
async def criar_usuario(usuario_schema:UsuarioSchema, session: Session =  Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail='E-mail já cadastrado')
    else:
        senha_cripitografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_cripitografada, usuario_schema.ativo, usuario_schema.adm)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuário cadastrado com sucesso {usuario_schema.email}"}


@auth_router.post('/login')
async def login(login_schema: LoginSchema, session: Session =  Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail='Usuario não encontrado ou credenciais invalidas')
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {"access_token": access_token, 'refresh_token': refresh_token ,'token_type': 'Bearer'}
    
@auth_router.post('/login-form')
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends() , session: Session =  Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail='Usuario não encontrado ou credenciais invalidas')
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {"access_token": access_token,'token_type': 'Bearer'}
    
@auth_router.get('/refresh')
async def use_refresh_token( usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {"access_token": access_token, 'token_type': 'Bearer'}
