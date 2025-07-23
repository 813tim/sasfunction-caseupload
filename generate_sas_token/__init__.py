import os
import logging
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('SAS Token Generator triggered.')

    case_id = req.params.get('caseId')
    if not case_id:
        return func.HttpResponse("Missing required parameter: caseId", status_code=400)

    account_name = os.environ.get("CASE_STORAGE_ACCOUNT")
    container_name = os.environ.get("CASE_STORAGE_CONTAINER")
    conn_string = os.environ.get("AzureWebJobsStorage")

    if not account_name or not container_name or not conn_string:
        return func.HttpResponse("Missing environment configuration", status_code=500)

    try:
        # Extract account key from connection string
        account_key = [x.split('=')[1] for x in conn_string.split(';') if x.startswith('AccountKey=')][0]
        blob_name = f"{case_id}/upload.txt"

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(write=True, create=True),
            expiry=datetime.utcnow() + timedelta(minutes=15)
        )

        sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        return func.HttpResponse(sas_url)

    except Exception as e:
        logging.error(f"Error generating SAS token: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
