from pydantic import BaseModel
from typing import List
class PRL_db (BaseModel):   
    
    filename: str
    sender: str
    subject: str
    time: str
    body: str
    ips: List[str] = []
    emails: List[str] = []
    domains:List[str] = []
    urls: List[str] = []
    headers_footers: List[str]= []
    