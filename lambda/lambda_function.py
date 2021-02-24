"""
 Copyright (C) 2020 Dabble Lab - All Rights Reserved
 You may use, distribute and modify this code under the
 terms and conditions defined in file 'LICENSE.txt', which
 is part of this source code package.
 
 For additional copyright information please
 visit : http://dabblelab.com/copyright
 """

import logging
import json
import random

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective, ClearQueueDirective, ClearBehavior)

# Initializing the logger and setting the level to "INFO"
# Read more about it here https://www.loggly.com/ultimate-guide/python-logging-basics/
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

""" 
Instructions to modify the code to play the stream of your choice:

1. Replace the current url with your stream url. Make sure that it has has a valid SSL certificate and starts with 'https' and not 'http'
2. Replace the title under metadata with the name of your stream or radio. Alexa speaks out this name before the stream begings.
3. Replace the subtitle under metadata with your streams tagline. It is displayed on screen enabled devices while the skill is playing.
4. Replace the url under metadata>art>sources with an album art image of your choice. It should be in png or jpg format of the size 512x512 pixels.
5. Replace the url under metadata>backgroundImage>sources with a background image of your choice. It should be in png or jpg format of the size 1200x800 pixels.
"""

# Audio stream metadata
STREAMS = [
  {
    "token": '1',
    "url": 'https://www.radiokrishna.com/RKC-Terni-HQ.m3u',
    "metadata": {
      "title": 'Dabble Radio',
      "subtitle": 'A subtitle for dabble radio',
      "art": {
        "sources": [
          {
            "contentDescription": 'example image',
            "url": 'https://s3.amazonaws.com/cdn.dabblelab.com/img/audiostream-starter-512x512.png',
            "widthPixels": 512,
            "heightPixels": 512
          }
        ]
      },
      "backgroundImage": {
        "sources": [
          {
            "contentDescription": 'example image',
            "url": 'https://s3.amazonaws.com/cdn.dabblelab.com/img/wayfarer-on-beach-1200x800.png',
            "widthPixels": 1200,
            "heightPixels": 800
          }
        ]
      }
    }
  }
]

# Intent Handlers

# This handler checks if the device supports audio playback
class CheckAudioInterfaceHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        if handler_input.request_envelope.context.system.device:
            return handler_input.request_envelope.context.system.device.supported_interfaces.audio_player is None
        else:
            return False

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = language_prompts["DEVICE_NOT_SUPPORTED"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

# This handler starts the stream playback whenever a user invokes the skill or resumes playback.
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self,handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self,handler_input):
        stream = STREAMS[0]
        return ( handler_input.response_builder
                    .speak("Starting {}".format(stream["metadata"]["title"]))
                    .add_directive(
                        PlayDirective(
                            play_behavior=PlayBehavior.REPLACE_ALL,
                            audio_item=AudioItem(
                                stream=Stream(
                                    token=stream["token"],
                                    url=stream["url"],
                                    offset_in_milliseconds=0,
                                    expected_previous_token=None),
                                metadata=stream["metadata"]
                            )
                        )
                    )
                    .set_should_end_session(True)
                    .response
                )

class ResumeStreamIntentHandler(AbstractRequestHandler):
    def can_handle(self,handler_input):
        return (is_request_type("PlaybackController.PlayCommandIssued")(handler_input)
                or is_intent_name("AMAZON.ResumeIntent")(handler_input)
                )
    def handle(self,handler_input):
        stream = STREAMS[0]
        return ( handler_input.response_builder
                    .add_directive(
                        PlayDirective(
                            play_behavior=PlayBehavior.REPLACE_ALL,
                            audio_item=AudioItem(
                                stream=Stream(
                                    token=stream["token"],
                                    url=stream["url"],
                                    offset_in_milliseconds=0,
                                    expected_previous_token=None),
                                metadata=stream["metadata"]
                            )
                        )
                    )
                    .set_should_end_session(True)
                    .response
                )

# This handler handles all the required audio player intents which are not supported by the skill yet. 
class UnhandledFeaturesIntentHandler(AbstractRequestHandler):
    def can_handle(self,handler_input):
        return (is_intent_name("AMAZON.LoopOnIntent")(handler_input)
                or is_intent_name("AMAZON.NextIntent")(handler_input)
                or is_intent_name("AMAZON.PreviousIntent")(handler_input)
                or is_intent_name("AMAZON.RepeatIntent")(handler_input)
                or is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)
                or is_intent_name("AMAZON.StartOverIntent")(handler_input)
                or is_intent_name("AMAZON.ShuffleOffIntent")(handler_input)
                or is_intent_name("AMAZON.LoopOffIntent")(handler_input)
                )
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["UNHANDLED"])
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

# This handler provides the user with basic info about the skill when a user asks for it.
# Note: This would only work with one shot utterances and not during stream playback.
class AboutIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AboutIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = random.choice(language_prompts["ABOUT"])
        reprompt = random.choice(language_prompts["ABOUT_REPROMPT"])
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_intent_name("AMAZON.CancelIntent")(handler_input)
            or is_intent_name("AMAZON.StopIntent")(handler_input)
            or is_intent_name("AMAZON.PauseIntent")(handler_input)
            )
    
    def handle(self, handler_input):
        return ( handler_input.response_builder
                    .add_directive(
                        ClearQueueDirective(
                            clear_behavior=ClearBehavior.CLEAR_ALL)
                        )
                    .add_directive(StopDirective())
                    .set_should_end_session(True)
                    .response
                )

class PlaybackStartedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)
    
    def handle(self, handler_input):
        return ( handler_input.response_builder
                    .add_directive(
                        ClearQueueDirective(
                            clear_behavior=ClearBehavior.CLEAR_ENQUEUED)
                        )
                    .response
                )

class PlaybackStoppedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ( is_request_type("PlaybackController.PauseCommandIssued")(handler_input)
                or is_request_type("AudioPlayer.PlaybackStopped")(handler_input)
            )
    
    def handle(self, handler_input):
        return ( handler_input.response_builder
                    .add_directive(
                        ClearQueueDirective(
                            clear_behavior=ClearBehavior.CLEAR_ALL)
                        )
                    .add_directive(StopDirective())
                    .set_should_end_session(True)
                    .response
                )

# This handler tries to play the stream again if the playback failed due to any reason.
class PlaybackFailedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)
    
    def handle(self,handler_input):
        stream = STREAMS[0]
        return ( handler_input.response_builder
                    .add_directive(
                        PlayDirective(
                            play_behavior=PlayBehavior.REPLACE_ALL,
                            audio_item=AudioItem(
                                stream=Stream(
                                    token=stream["token"],
                                    url=stream["url"],
                                    offset_in_milliseconds=0,
                                    expected_previous_token=None),
                                metadata=stream["metadata"]
                            )
                        )
                    )
                    .set_should_end_session(True)
                    .response
                )
    

# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


class ExceptionEncounteredRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("System.ExceptionEncountered")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Interceptors

# This interceptor is used for supporting different languages and locales. It detects the users locale,
# loads the corresponding language prompts and sends them as a request attribute object to the handler functions.
class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        
        try:
            with open("languages/"+str(locale)+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ str(locale[:2]) +".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts

# This interceptor logs each request sent from Alexa to our endpoint.
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

# This interceptor logs each response our endpoint sends back to Alexa.
class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))

# This exception handler handles syntax or routing errors. If you receive an error stating 
# the request handler is not found, you have not implemented a handler for the intent or 
# included it in the skill builder below
class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# Skill Builder
# Define a skill builder instance and add all the request handlers,
# exception handlers and interceptors to it.

sb = SkillBuilder()
sb.add_request_handler(CheckAudioInterfaceHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ResumeStreamIntentHandler())
sb.add_request_handler(UnhandledFeaturesIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(AboutIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(PlaybackStartedIntentHandler())
sb.add_request_handler(PlaybackStoppedIntentHandler())
sb.add_request_handler(PlaybackFailedIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()
