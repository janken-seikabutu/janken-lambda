from fastapi import APIRouter

import os
from os.path import join, dirname
from dotenv import load_dotenv

import boto3
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr

import json
from pydantic import BaseModel
import time

import random

def markov_game(event, context):
  json_ob = event["body"]
  markov = json.dumps(json_ob)
  markov_previous_id = markov["previous_id"]
  score_table = dynamodb.Table("janken-scores")
  previous_result = score_table.get_item(
    Key={"id":markov_previous_id}
  )
  previous_hand_and_result = previous_result["Item"]["hand"] + previous_result["Item"]["result"] + "-"

  rock = previous_hand_and_result + "g"
  scissors = previous_hand_and_result + "c"
  paper = previous_hand_and_result + "p"

  markov_id = markov["markov_id"]
  markov_table = dynamodb.Table("janken-markov")
  markov_result = markov_table.get_item(
    Key = {"id":markov_id}
  )

  count_rock = markov_result["Item"][f"{rock}"]
  count_scissors = markov_result["Item"][f"{scissors}"]
  count_paper = markov_result["Item"][f"{paper}"]

  counter = [count_rock, count_scissors, count_paper]
  max_index = [i for i, x in enumerate(counter) if x == max(counter)]

  hands = ["g", "c", "p"]
  choice_hand = random.choice(max_index)
  if choice_hand - 1 == -1:
    hand_ai = "p"
  else:
    hand_ai = hands[choice_hand - 1]

  game_result = ""

  if markov["hand"] == hand_ai:
    game_result = "d"
  elif markov.hand == "g":
    if hand_ai == "c":
      game_result = "w"
    else:
      game_result = "l"

  elif markov["hand"] == "c":
    if hand_ai == "p":
      game_result = "w"
    else:
      game_result = "l"

  else:
    if hand_ai == "g":
      game_result = "w"
    else:
      game_result = "l"
  
  attribut_name = previous_hand_and_result + markov["hand"]

  markov_table.update_item(
    Key = {"id":markov_id},
    UpdateExpression = "set #result = :count",
    ExpressionAttributeNames = {"#result":attribut_name},
    ExpressionAttributeValues = {":count" : markov_result["Item"][f"{attribut_name}"] + 1}
  )

  count_scores = score_table.scan()
  score_id = count_scores["Count"] + 1
  score_table.put_item(
    Item={
      "id": score_id,
      "user_name": markov["name"],
      "hand": markov["hand"],
      "result": game_result,
      "game_id": 2,
    }
  )
  user_name = markov["name"]
  game_count = score_table.scan(
    FilterExpression = Attr("user_name").eq(f"{user_name}")
  )

  user_table = dynamodb.Table("janken-users")
  user_table.update_item(
    Key = {"name":user_name},
    UpdateExpression = "set previous_id = :previous_id, game_count = :game_count",
    ExpressionAttributeValues = {":previous_id" : score_id, ":game_count" : game_count["Count"]},
  )

  return {"previous_id":score_id, "game_count":game_count["Count"], "result":game_result, "hand_ai":hand_ai}
