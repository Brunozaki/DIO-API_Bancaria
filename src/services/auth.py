from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

SEGREDO_JWT = "segredo_super_secreto"
ALGORITMO_JWT = "HS256"
TEMPO_EXPIRACAO_MIN = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def criar_hash_senha(senha: str) -> str:
    """Gera o hash da senha."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return pwd_context.verify(senha, hash_senha)


def criar_token_jwt(dados: dict) -> str:
    """Cria um token JWT com tempo de expiração."""
    dados_copia = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=TEMPO_EXPIRACAO_MIN)
    dados_copia.update({"exp": expiracao})
    return jwt.encode(dados_copia, SEGREDO_JWT, algorithm=ALGORITMO_JWT)


def verificar_token_jwt(token: str) -> dict:
    """Valida o token JWT e retorna os dados."""
    try:
        return jwt.decode(token, SEGREDO_JWT, algorithms=[ALGORITMO_JWT])
    except JWTError:
        return None
