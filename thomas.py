import urllib2
import json
import os 
import sys 
import pymysql 
import boto3 
import logging 

conn = pymysql.connect(host = 'uvaclasses.martyhumphrey.info', 
                       port = 3306, 
                       user = 'UVAClasses', 
                       passwd = 'TalkingHeads12', 
                       db = 'uvaclasses')

cur = conn.cursor() 

API_BASE="http://bartjsonapi.elasticbeanstalk.com/api"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.eee4d2fa-759c-4eb2-837f-53a6f0d9e3f2"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "getCourseName":
        return get_course_name(intent)
    elif intent_name == "getSeats":
        return get_spots(intent)
    elif intent_name == "getInstructor":
        return get_instructor(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Thomas Scheduling - Thanks"
    speech_output = "Thank you for using the Thomas Course Scheduling skill. See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "BART"
    speech_output = "Welcome to the Alexa Thomas Course Scheduling skill. " \
                    "Given a course number, you can ask me for the course title, or " \
                    "ask me for the instructor of the course, or " \
                    "ask me for the number of available seats of the course." 
    reprompt_text = "Please ask me for a course number, " \
                    "for example CS 47 40."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_course_name(intent):
    class_num = intent['slots']['courseNum']['value']
    session_attributes = {} 
    card_title = "Thomas Course Name Retrieval System"
    reprompt_text = "" 
    should_end_session = False 
    course_title = '' 
    
    cur.execute("SELECT DISTINCT Title FROM CS1188Data WHERE Number = '" + class_num + "'")
    for classes in cur: 
        course_title += classes[0] 

    speech_output = "The title for this class is " + course_title + "." 
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_instructor(intent):
    class_num = intent['slots']['courseNum']['value']
    session_attributes = {} 
    card_title = "Thomas Instructor Name Retrieval System"
    reprompt_text = "" 
    should_end_session = False 
    this_professor = ''
    
    cur.execute("SELECT DISTINCT Instructor FROM CS1188Data WHERE Number = '" + class_num + "'")
    
    for instructors in cur: 
        this_professor += (instructors[0] + ", ") 

    speech_output = "Dr. " + this_professor + " teach this class. " 

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_spots(intent):
    class_num = intent['slots']['courseNum']['value']
    session_attributes = {} 
    card_title = "Thomas Available Seats Retrieval System"
    reprompt_text = "" 
    should_end_session = False 
    open_seats = ''

    cur.execute("SELECT Section, EnrollmentLimit - Enrollment FROM CS1188Data WHERE Number = '" + class_num + "'") 

    for spots in cur: 
        section = spots[0]
        seats = spots[1] 
        open_seats += "Section " + str(spots[0]) + " has " + str(spots[1]) + " seats available."
    
    speech_output = open_seats 
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }


