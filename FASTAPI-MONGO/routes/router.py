import re
import email
import traceback
from mongo_wrapper import MongoWrapper
from fastapi import APIRouter, File, UploadFile
from models.ioc import PRL_db
from schema.schemas import list_serial
from fastapi import HTTPException, status
from bson import ObjectId
from bson.objectid import ObjectId
from pymongo.results import DeleteResult

router = APIRouter()


@router.get("/iocs/")
async def get_iocs(required_param: str, page_limit: int, page_offset: int):
    if required_param not in ["urls", "ips", "domains", "emails"]:
        raise Exception(f"Invalid query param: {required_param}")
    mongo_wrapper = MongoWrapper()
    iocs = list_serial(mongo_wrapper.mail_info.find())
    result = []
    for ioc in iocs:
        result.extend(list(set(ioc.get(required_param, []))))

    skip = (page_offset - 1) * page_limit
    return result[skip: skip + page_limit]


async def extract_info(ioc_file: UploadFile) -> dict:
    mongo_wrapper = MongoWrapper()
    try:
        file = await ioc_file.read()
        msg = email.message_from_bytes(file)
       
        sender = msg["From"]
        subject = msg["Subject"]
        time = msg["Date"]

       
        body_parts = []
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                body_parts.append(part.get_payload(decode=True))

        body_content = b"\n".join(body_parts).decode("ISO-8859-1")

      
        if body_content:
            body_content = body_content.strip()
        
            ips = list(
                set(re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", body_content))
            )
            emails = list(
                set(
                    re.findall(
                        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,4}",
                        body_content,
                    )
                )
            )
            domains = list(
                set(
                    re.findall(
                        r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
                        body_content,
                    )
                )
            )
                          
            pattern = r'\.exe$|\.html|\.pdf|\.lnk|\.zip|\.jpg|\.png|\.EXE|\.LNK|\.PDF|\.ZIP|\.JPG|\.PNG|\.GOV|\.GOV.IN|\.gov|\.gov.in|\.certain|\.org.in$'
            filtered_domains = [s for s in domains if not re.search(pattern, s)]
                
            urls = list(set(re.findall(r"https?://[^\s]+", body_content)))
            
            extracted_data: PRL_db = {
                "filename": ioc_file.filename,
                "sender": sender,
                "subject": subject,
                "time": time,
                "body": body_content,
                "ips": ips,
                "emails": emails,
                "domains": filtered_domains,
                "urls": urls,
                "headers_footers": [],
            }

            mongo_wrapper.mail_info.insert_one(extracted_data)
            return extracted_data

    except Exception as e:
        print({traceback.print_exc()})


@router.post("/ioc/", response_model=PRL_db)
async def create_item(ioc_file: UploadFile):
    """
    POST /ioc
    """
    result = await extract_info(ioc_file)
    return result


@router.delete("/ioc/{id}/")
async def delete_ioc(id: str):
    """
    DELETE /ioc/{ioc_id}
    """
    mongo_wrapper = MongoWrapper()
    deletion_result: DeleteResult = mongo_wrapper.mail_info.find_one_and_delete({"_id": ObjectId(id)})
    
    if deletion_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IoC with id {id} not found",
        )
    else:
        return {"message": f"IoC with id {id} deleted successfully"}

@router.put("/ioc/{id}/", response_model=PRL_db)
async def update_ioc(id: str, ioc_file: UploadFile):
    """
    PUT /ioc/{ioc_id}
    """
    mongo_wrapper = MongoWrapper()
    existing_ioc =  mongo_wrapper.mail_info.find_one({"_id": ObjectId(id)})
    if existing_ioc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IoC with id {id} not found",
        )
    
    result = await extract_info(ioc_file)
    
  
    await mongo_wrapper.mail_info.update_one(
        {"_id": ObjectId(id)},
        {"$set": result}
    )
    
    return result
