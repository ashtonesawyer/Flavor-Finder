# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import random
import requests
import json

# for DynamoDB
import os
import boto3

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

'''ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')

ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)'''

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can ask me for a recommendation, to review a recipe, or for help. Which would you like to try?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello there!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can get a recommendation for what recipe to try! You can tell me about what ingredients you have, how long you have, what meal it's for \
            or what cuisine you want. You can also review recipes that you have tried and give me notes that I'll remind you of so it's even better the \
            next time you make it. How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

# ****************************************
# ********** Custom Intents **************
headers = {
    'X-RapidAPI-Key': "get_key_to_use",        # put person access key here
    'X-RapidAPI-Host': "tasty.p.rapidapi.com"
    }

# Input (optional): meal (string), time (duration), ingredient (string), cuisine (string)
# Gets recipes, filters based on input, and randomly chooses one from those that match
class RecommendMealIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RecommendMealIntent")(handler_input)
        
    def handle(self, handler_input):
        # slot setup
        slots = handler_input.request_envelope.request.intent.slots
        cuisine = slots['cuisine'].value
        time = slots['time'].value
        ingredients = slots['ingredients'].value
        meal = slots['meal'].value
        
        #TastyAPI setup
        # To check valid tags: print(requests.request("GET", tags_url, headers=headers))
        tags_url = "https://tasty.p.rapidapi.com/tags/list"
        list_url = "https://tasty.p.rapidapi.com/recipes/list"
        
        #from: starting offset, size: how many recipes to collect, tags: filter, q: filter by ingredient
        # randrange to prevent the same recipes being selected every time
        querystring = {'from':str(random.randrange(10)), 'size':"20", 'tags':"", 'q': ""}
        
        recipe_list = {'count': 0, 'results':[]}  # acceptable recipes
        # recipes that fit a single filter
        meal_filter = None
        cuisine_filter = None
        time_filter = None
        
        if ingredients:
            querystring['q'] = ingredients
            
        if meal:
            meal_filter = [0]
            meal_filter += self.process_meal(meal, list_url, querystring)
        
        if cuisine:
            cuisine_filter = [0]
            cuisine_filter += self.process_cuisine(cuisine, list_url, querystring)
            
        if time:
            # convert duration to time in minutes (int)
            if "T" in time:
                mins = 0 
                if "H" in time:
                    h = time.find("H")
                    mins += int(time[2:h]) * 60
                    if "M" in time:
                        m = time.find("M")
                        mins += int(time[h+1:m])
                elif "M" in time:
                    mins += int(time[2:-1])
                    
                if mins <= 60:
                    time_filter = [0]
                    time_filter += self.process_time(mins, list_url, querystring)
            
        # get final list of possible recipes
        if meal_filter and cuisine_filter and time_filter:
            for recipe in meal_filter:
                if recipe in cuisine_filter and recipe in time_filter:
                    recipe_list['results'] += [recipe]
        elif meal_filter and cuisine_filter:
            for recipe in meal_filter:
                if recipe in cuisine_filter:
                    recipe_list['results'] += [recipe]
        elif meal_filter and time_filter:
            for recipe in meal_filter:
                if recipe in time_filter:
                    recipe_list['results'] += [recipe]
        elif time_filter and cuisine_filter:
            for recipe in time_filter:
                if recipe in cuisine_filter:
                    recipe_list['results'] += [recipe] 
        elif meal_filter:
            recipe_list['results'] += meal_filter[1:]
        elif time_filter:
            recipe_list['results'] += time_filter[1:]
        elif cuisine_filter:
            recipe_list['results'] += cuisine_filter[1:]
        # if no filters then any recipes are acceptable
        else:
            response = requests.request("GET", list_url, headers=headers, params=querystring)
            response = json.loads(response.text)
            recipe_list['results'] += response['results']
        
        recipe_list['count'] += len(recipe_list['results'])
        
        # respond
        if (recipe_list['count'] == 0):
            speak_output = "Sorry, I wasn't able to find any recipes that meet all of your needs."
        else:
            i = random.randrange(0, recipe_list['count'])
            speak_output = "I recommend making " + recipe_list['results'][i]['name'] + ". Have a good day!"
            
        return (handler_input.response_builder.speak(speak_output).response)
        
    def process_meal(self, inputs, list_url, querystring):
        tmp = []
        
        if inputs == "snack":
            querystring['tags'] = "snacks"
            response = requests.request("GET", list_url, headers=headers, params=querystring)
            response = json.loads(response.text)
            tmp += response['results']
            
            querystring['tags'] = "bakery_goods"
            response = requests.request("GET", list_url, headers=headers, params=querystring)
            response = json.loads(response.text)
            tmp += response['results']
            
        else:
            if inputs == "dessert" or inputs == "appetizer":
                inputs += "s"
            
            querystring['tags'] = inputs
            response = requests.request("GET", list_url, headers=headers, params=querystring)
            response = json.loads(response.text)
            tmp += response['results']
        
        return tmp
    
    def process_cuisine(self, inputs, list_url, querystring):
        # from tasty
        cuisines = ["Chinese",
                    "German",
                    "Japanese",
                    "Middle Eastern",
                    "Seafood",
                    "Thai",
                    "Hawaiian",
                    "Indigenous",
                    "Cuban",
                    "Venezuelan",
                    "British",
                    "Fusion",
                    "Taiwanese",
                    "Laotian",
                    "Jamaican",
                    "Puerto Rican",
                    "Vietnamese",
                    "African",
                    "South African",
                    "West African",
                    "Swedish",
                    "Haitian",
                    "Soul Food",
                    "French",
                    "Korean",
                    "Latin American",
                    "Ethiopian",
                    "Persian",
                    "American",
                    "Brazilian",
                    "Greek",
                    "Indian",
                    "Italian",
                    "Mexican",
                    "Caribbean",
                    "Filipino",
                    "Kenyan",
                    "Lebanese",
                    "Peruvian",
                    "Dominican"]
                    
        for name in cuisines:
            if name in inputs or inputs in name:
                tmp = name.lower()
                if " " in tmp:
                    tmp.replace(" ", "_")
                
                querystring['tags'] = tmp
                break
                
        response = requests.request("GET", list_url, headers=headers, params=querystring)
        response = json.loads(response.text)
        return response['results'] 
    
    def process_time(self, inputs, list_url, querystring):
        if inputs <= 15:
            querystring['tags'] = "under_15_minutes"
        elif inputs <= 30:
            querystring['tags'] = "under_30_minutes"
        elif inputs <= 45:
            querystring['tags'] = "under_45_minutes"
        else:
            querystring['tags'] = "under_1_hour"
            
        response = requests.request("GET", list_url, headers=headers, params=querystring)
        response = json.loads(response.text)
        return response['results']


# User review options:
#   1. likes
#   2. likes/willing to retry with corrections
#   3. dislikes
# Input (required): recipe (string)
class ReviewRecipeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ReviewRecipeIntent")(handler_input)
        
    def handle(self, handler_input):
        speak_output = "Sure, let's review it. Did you like this recipe?"
        # user response - ex. "Yes", "yes, but {notes}", "no"
        # alexa response - ex. "I'm glad you liked it, thanks for telling me", "I've made a note of those adjustments and will
        #   remind you of them the next time you make it", "I'm sorry that recipe didn't work out. I'll make sure to leave that one out next time."
        
        return (handler_input.response_builder.speak(speak_output).ask(speak_output).response)

# Follow up intents - not set up to only activate after ReviewRecipe

# Input (optional): notes (string)
class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("YesIntent")(handler_input)
        
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        notes = slots['notes'].value
        
        speak_output = "I'm glad you liked it! "
        if notes:
            speak_output += "I've made a note of those adjustments and will remind you of them the next time you make it."
        
        # store notes with recipe (DymanoDB?)
        
        return (handler_input.response_builder.speak(speak_output).response)

# No input
class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NoIntent")(handler_input)
        
    def handle(self, handler_input):
        speak_output = "I'm sorry that recipe didn't work out. I'll make sure to leave it out next time."
        
        # store disliked with recipe (DynamoDB?)
        
        return (handler_input.response_builder.speak(speak_output).response)

# ********* End Custom *******************
# ****************************************

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(RecommendMealIntentHandler())
sb.add_request_handler(ReviewRecipeIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
