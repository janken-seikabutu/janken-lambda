import json

import os

import boto3
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr

import json
import hashlib

session = Session(
  aws_access_key_id=os.environ["AWS_DYNAMODB_ACCESSKEY"],
  aws_secret_access_key=os.environ["AWS_DYNAMODB_SECRETKEY"],
  region_name=os.environ["AWS_DYNAMODB_REGION"])

dynamodb = session.resource("dynamodb")

def register_user(event, context):
  user = json.loads(event)
  register_table = dynamodb.Table("janken-users")
  confilm = register_table.scan(
    FilterExpression = Attr("name").eq(f"{user["name"]}")
  )
  if confilm["Count"] == 0:
    register_pass_hash = hashlib.sha256()
    register_pass_hash.update(user["password"].encode())
    response = register_table.put_item(
      Item={
        "name": user["name"],
        "password": register_pass_hash.hexdigest(),
        "markov_id": 0,
        "game_count": 0,
        "previous_id": 0,
      }
    )
    return json.dumps({"name":user["name"], "markov_id":0, "game_count":0, "previous_id":0})
  return json.dumps({"error":"そのユーザーはすでに登録されています。別のユーザー名で登録してください。"})