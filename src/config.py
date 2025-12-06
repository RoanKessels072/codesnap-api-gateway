from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "api-gateway"
    port: int = 5000
    
    nats_url: str = "nats://nats:4222" 
    
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "codesnap"
    keycloak_client_id: str = "codesnap-client"
    
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()