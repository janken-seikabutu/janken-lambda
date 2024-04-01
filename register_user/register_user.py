import json

def register_user(event, context):
  # ログを出力する
  print("event:", event)
  print("context:", context)
  return json.dumps(event)
