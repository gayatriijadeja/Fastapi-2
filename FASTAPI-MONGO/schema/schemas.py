def individual_serial(ioc) -> dict:
    return {
        "id": str(ioc["_id"]),
        "filename": ioc["filename"],
        "sender": ioc["sender"],
        "subject": ioc["subject"],
        "time": ioc["time"],
        "body": ioc["body"],
        "ips": ioc["ips"],
        "emails": ioc["emails"],
        "domains": ioc["domains"],
        "urls": ioc["urls"],
    }

def list_serial(iocs) -> list:
    return [individual_serial(ioc) for ioc in iocs] 

def serializeDict(PRL_db) -> dict:
    return {**{i: str(PRL_db[i]) for i in PRL_db if i=="_id"},**{i : PRL_db[i] for i in PRL_db if i!="_id"}} 

def serializeList(iocs) -> list:
    return [serializeDict(a) for a in iocs ]
