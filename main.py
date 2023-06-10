from fastapi import FastAPI
from transformers import pipeline
from dotenv import dotenv_values
import requests
from requests.auth import HTTPBasicAuth

app = FastAPI()

env_vars = dotenv_values(".env")
epicor_api_url = env_vars['EPICOR_API_URL']
epicor_user_id = env_vars['EPICOR_USER_ID']
epicor_password = env_vars['EPICOR_PASSWORD']
epicor_company = env_vars['EPICOR_COMPANY']

summarizer = pipeline(task="summarization")

@app.post("/order-comment")
async def order_comment(order_num: str):

    def get_sales_order_comment():
        url = f'{epicor_api_url}/Erp.BO.SalesOrderSvc/SalesOrders({epicor_company}, {order_num})?$select=OrderComment'
        headers = {
            'Content-Type': 'application/json'
        }
        auth = HTTPBasicAuth(epicor_user_id, epicor_password)

        try:
            response = requests.get(url, auth=auth, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

   
    response = get_sales_order_comment()
    
    if "error" in response:
        return response

    comment = response.get('OrderComment', '')
    
    result = summarizer(comment)
    
    summary = result[0]['summary_text']
    
    return {"summary": summary}
