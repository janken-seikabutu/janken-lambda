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

def login_user(event, context):
  json_ob = event["body"]
  user = json.loads(json_ob)
  login_table = dynamodb.Table("janken-users")
  result = login_table.scan(
    FilterExpression = Attr("name").eq(f"{user["name"]}")
  )
  if result["Count"] != 0:
    login_pass_hash = hashlib.sha256()
    login_pass_hash.update(user["password"].encode())
    if result["Items"][0]["password"] == login_pass_hash.hexdigest():
      markov_id = result["Items"][0]["markov_id"]
      game_count = result["Items"][0]["game_count"]
      previous_id = result["Items"][0]["previous_id"]
      return {"name":user["name"], "markov_id":markov_id, "game_count":game_count, "previous_id":previous_id}
    else:
      return {"error":"パスワードが間違っています。"}
  return {"error":"ユーザー名が間違っています。登録したユーザー名を入力してください。登録がまだの場合はユーザー登録をしてください。"}