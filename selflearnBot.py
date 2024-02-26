#!pip install difflib

import json
from difflib import get_close_matches

#! /usr/bin/python3
from flask import Flask, render_template, request
import random
import csv
import os
from botConfig import myBotName, chatBG, botAvatar, useGoogle, confidenceLevel, knownBase
from botRespond import getResponse
from urllib.parse import unquote
import urllib.parse
##Experimental Date Time
from dateTime import getTime, getDate

app = Flask(__name__)

chatbotName = 'Demo ChatBot'
botAvatar = '/static/bot.png'


def load_knowledge_base(file_path: str) -> dict:
  with open(file_path, 'r') as file:
    data: dict = json.load(file)
  return data

def save_knowledge_base(file_path: str, data: dict):
  with open(file_path, 'w') as file:
    json.dump(data, file, indent=2)

def find_best_match(user_questions: str, questions: list[str]) -> str|None:
  matches: list= get_close_matches(user_questions, questions, n=2, cutoff=0.6)
  return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str|None:
  for q in knowledge_base["questions"]:
    if q["question"] == question:
      return q["answer"]

def selfTrainBot(user_input):

    knowledge_base:dict = load_knowledge_base('knowledge_base.json')
    best_match: str | None = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
    if best_match:
      answer: str = get_answer_for_question(best_match, knowledge_base)
      print(f'Bot: {answer}')
      return answer
    else:
      botResponse:str = "I dono know the response. Can you Teach me. Write n mentioned pattern \"question:\" Whom am i. \"answer:\" I am a chatbot.ELSE \"skip\" to skip:"
      print('Bot: I dont\'t know the answer. Can you teach me? Type the answer with prefix as "answer<space> <your answer>"or "skip" to skip: ')
      #new_answer: str = input('Type the answer with prefix as "answer<space>"or "skip" to skip: ')
      return botResponse
      if new_answer.lower() != 'skip':
        knowledge_base["questions"].append({"question":user_input, "answer": new_answer})
        save_knowledge_base('knowledge_base.json', knowledge_base)
        print('Bot: Thank you! I learned a new response!')


def chatbot():
  knowledge_base:dict = load_knowledge_base('knowledge_base.json')

  while True:
    user_input:str = input('You:')

    if(user_input.lower() =='quit'):
      break

    best_match: str | None = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
      answer: str = get_answer_for_question(best_match, knowledge_base)
      print(f'Bot: {answer}')
    else:
      print('Bot: I dont\'t know the answer. Can you teach me?')
      new_answer: str = input('Type the answer or "skip" to skip: ')

      if new_answer.lower() != 'skip':
        knowledge_base["questions"].append({"question":user_input, "answer": new_answer})
        save_knowledge_base('knowledge_base.json', knowledge_base)
        print('Bot: Thank you! I learned a new response!')

def remove_prefix(str, prefix):
    return str.lstrip(prefix)

def tryGoogle(myQuery):
    myQuery = myQuery.replace("'", "%27")
    showQuery = urllib.parse.unquote(myQuery)
    return "<br><br>You can try this from my friend Google: <a target='_blank' href='https://www.google.com/search?q=" + myQuery + "'>" + showQuery + "</a>"



@app.route("/")
def home():
    return render_template("index.html", botName = chatbotName, botAvatar = botAvatar)

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    
    botReply = str(getResponse(userText))
    if botReply == "IDKresponse":
      text = userText.split('answer:')
      if text[0].startswith('question:'):
        questionText = str(remove_prefix(text[0], 'question:'))
        newAnswer = text[1].strip()
        knowledge_base:dict = load_knowledge_base('knowledge_base.json')
        knowledge_base["questions"].append({"question":unquote(questionText.strip()), "answer": unquote(newAnswer)})
        save_knowledge_base('knowledge_base.json', knowledge_base)
        print('Bot: Thank you! I learned a new response!')
        botReply ='Thank you! I learned a new response!'
       
      else:    
        botReply = str(selfTrainBot(userText))
        
    elif botReply != 'IDKresponse':
                
      if botReply == "getTIME":
              botReply = getTime()
              print(getTime())
      if botReply == "getDATE":
              botReply = getDate()
              print(getDate())
        #botReply = str(getResponse('IDKnull')) ##Send the i don't know code back to the DB       
        #noResponse = ["I don't know.", "I'm not sure about that.", "Is there a different way you can ask that?","I don't have a response for that.","I will have to give that some thought.","I don't really know what you are asking."]
        #botReply = random.choice(noResponse)
    elif useGoogle == "yes":
          botReply = botReply + tryGoogle(userText)
            
    return botReply

if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=80)




#if __name__ == '__main__':
#  chatbot()