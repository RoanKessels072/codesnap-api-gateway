import nats
from nats.aio.client import Client as NATS
import json
from src.config import settings

class NATSClient:
    def __init__(self):
        self.nc: NATS = None
        
    async def connect(self):
        self.nc = await nats.connect(settings.nats_url)
        print(f"Connected to NATS at {settings.nats_url}")
        
    async def close(self):
        if self.nc:
            await self.nc.close()
            
    async def request(self, subject: str, data: dict, timeout: float = 5.0):
        if not self.nc:
            raise Exception("NATS not connected")
        
        try:
            response = await self.nc.request(
                subject, 
                json.dumps(data).encode(),
                timeout=timeout
            )
            return json.loads(response.data.decode())
        except TimeoutError:
            return {"error": "Service request timed out"}
        except Exception as e:
            return {"error": str(e)}

nats_client = NATSClient()