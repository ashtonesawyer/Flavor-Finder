# Flavor-Finder
# Overview
This is the interaction model and (unfinished) fulfillment of an Alexa skill to recommend a recipe. It is comprised of 2 main intents, Recommend a Recipe 
and Review a Recipe. For Winter23 CS466 - Voice Assistants.
## Recommend a Recipe
### Description
The slots for this intent are the meal (breakfast, lunch, etc), cuisine, time available and an available ingredient. A more fully implimented 
version would be able to take a list of ingredients. None of the slots are required and they can be used in any combination. The recipes are 
provided by TastyAPI. 
### Known Errors
Because the TastyAPI also has articles that are compilations of recipes, occationally the recommended recipe is one of these compilations. 
I'm not sure of the best way to filter these compilations out. 
### Future 
A finished version of this would also take into account the user's tastes (as gathered from the Review a Recipe intent) to avoid recommending
recipes that the user has said they disliked. 
## Review a Recipe
### Description
This is a 2 turn intent that takes in the name of a recipe (a required slot) and asks whether or not the user liked the recipe. 
There are 3 followup intents based on the user's answer.
1. They liked the recipe:

In this case, the fact that the user liked the recipe should be saved along with the recipe for future reference. 

2. They liked the recipe with modifications:

In this case, the user would give notes to be stored verbatum with the recipe in question so that the next time it was recommended they would be reminded
of the changes that they wanted to make.

3. They disliked the recipe:

In this case, the fact that the user disliked the recipe would be stored with it in order to prevent it being recommended again. 
### Known Errors
This is the most sparsely implimented part of the skill. Alexa will speak as though the information is being saved, but that funcitonality has not been set up. 
The followup intents are also not set to only be activated after the main Review a Recipe intent, and as such can be activated any time the user speaks, leading to 
potentially confusing conversation. 

It should also be noted that the values given for the recipe slot are names that have been scraped from AllRecipes, not necessarily names of recipes that can be 
found using the TastyAPI. These should either be replaced by a list of the names of every recipe in the API, or (ideally) should be dynamic and added to as the user tries different recipes. I don't know if adding slots during use is possible. 
### Future
This intent simply needs to be finished, likely by connecting it to the DynamoDB in order to store the user input. The required imports and the 
necessary changes in requirements.txt in order to use the DynamoDB have been made, but implimentation has not been started. 

# Use
To use, you need to have an Amazon Developer account and create the skill. You also need an AWS account in order to use Amazon's NLP functions. 
In order to use the TastyAPI, you'll need to subscribe and get your own access key. All of these are free below a certain threshold of use. 

Development is most easily done in the Amazon Development Console, though it can also be done in VS Code using the Alexa Skills Kit. To get to the Alexa 
development console, click the link below, create an account, and select 'Alexa Skills Kit'.
# Testing
No automated tests have been written for this project. All testing has been done manually in the Amazon Develop Console's testing UI. 
# Helpful Links
* [Amazon Developer Console](https://developer.amazon.com/dashboard)
* [AWS](https://aws.amazon.com/)
* [ASK Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
* [TastyAPI](https://rapidapi.com/apidojo/api/tasty)
