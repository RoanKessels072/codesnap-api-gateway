from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import requests
from src.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthHandler:
    def __init__(self):
        self.public_key = None
    
    def get_public_key(self):
        if self.public_key:
            return self.public_key
            
        try:
            url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.public_key = f"-----BEGIN PUBLIC KEY-----\n{data['public_key']}\n-----END PUBLIC KEY-----"
            print("Successfully fetched Keycloak public key")
            return self.public_key
        except Exception as e:
            print(f"Failed to fetch Keycloak public key: {e}")
            return None

auth_handler = AuthHandler()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    public_key = auth_handler.get_public_key()
    if not public_key:
        raise HTTPException(status_code=500, detail="Auth configuration error")

    try:
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"], 
            audience="account"
        )
        
        user_data = {
            "keycloak_id": payload.get("sub"),
            "username": payload.get("preferred_username"),
            "email": payload.get("email"),
            "roles": payload.get("realm_access", {}).get("roles", [])
        }
        return user_data
        
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception