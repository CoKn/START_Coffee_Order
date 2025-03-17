import os
import requests
import logging
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class NotionAdapter:
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('NOTION_ACCESS_TOKEN')

    @property
    def headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }

    def query(_self, database_id: str, filter=None):
        """
        The database id is the first number in the page link

        :param database_id:
        :param filter:
        :return:
        """
        if filter is None:
            filter = {}
        url = f'https://api.notion.com/v1/databases/{database_id}/query'
        if not _self.access_token:
            logging.error("No Notion access token provided.")
            return None
        response = requests.post(url, headers=_self.headers, json=filter)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Query error: {response.json()}")
            return {"error": response.status_code}

    def update_page(self, page_id: str, data: dict):
        url = f'https://api.notion.com/v1/pages/{page_id}'
        if not self.access_token:
            logging.error("No Notion access token provided.")
            return None
        response = requests.patch(url, headers=self.headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Update error: {response.json()}")
            return {"error": response.status_code}

    def get_page(self, page_id: str):
        url = f'https://api.notion.com/v1/pages/{page_id}'
        if not self.access_token:
            logging.error("No Notion access token provided.")
            return None
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Get page error: {response.json()}")
            return {"error": response.status_code}

    def create_page(self, database_id: str, properties: dict, icon: dict = None, cover: dict = None, children: list = None):
        url = 'https://api.notion.com/v1/pages'
        data = {
            "parent": { "database_id": database_id },
            "properties": properties
        }
        if icon:
            data["icon"] = icon
        if cover:
            data["cover"] = cover
        if children:
            data["children"] = children

        if not self.access_token:
            logging.error("No Notion access token provided.")
            return None

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Create page error: {response.json()}")
            return {"error": response.status_code}

    def __hash__(self):
        return hash(self.access_token)

    def __eq__(self, other):
        if isinstance(other, NotionAdapter):
            return self.access_token == other.access_token
        return False