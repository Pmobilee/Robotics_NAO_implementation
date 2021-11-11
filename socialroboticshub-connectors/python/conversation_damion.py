import openai
import speech_recognition as sr
import os

TEXT = True

openai.api_key = os.getenv('GPT3_KEY')

CONVERSATION = "The following is a conversation with an AI assistant called Nao. Nao is helpful, creative, clever, and very friendly.\n\nNao: Hi I am Nao. What is your name?"

def add_to_conv(C, text, human = True):
    if human:
        C += f"\nHuman:{text}\nNao:"
    else:
        C += f"{text}"
    return C

def get_action(text):

    if 'blue' in text.lower():
        example.action_runner.run_waiting_action('say_animated', 'Activated blue colour scheme')
        example.action_runner.run_waiting_action('set_eye_color', 'blue')
        example.action_runner.run_waiting_action('set_ear_color', 'blue')
        example.action_runner.run_waiting_action('set_head_color', 'blue')

    if 'fist' in text.lower:
        example.action_runner.run_waiting_action('do_gesture', 'fistbump')
    
        
        
        


# response = openai.Completion.create(
#   engine="davinci",
#   prompt=CONVERSATION,
#   temperature=0.9,
#   max_tokens=150,
#   top_p=1,
#   frequency_penalty=0.0,
#   presence_penalty=0.6,
#   stop=["\n", " Human:", " AI:"]
# )
response = 'default '
print(response)



    # Get human input


from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector


class Example:
    """Example that uses speech recognition. Prerequisites are the availability of a dialogflow_key_file,
    a dialogflow_agent_id, and a running Dialogflow service. For help meeting these Prerequisites see
    https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/260276225/The+Social+Interaction+Cloud+Manual"""

    __CONVERSATION = "The following is a conversation with an AI assistant called Nao. Nao is helpful, creative, clever, and very friendly.\n\nNao: Hi I am Nao. What is your name?"
    def __init__(self, server_ip: str, dialogflow_key_file: str, dialogflow_agent_id: str):
        self.sic = BasicSICConnector(server_ip, 'en-US', dialogflow_key_file, dialogflow_agent_id)
        self.action_runner = ActionRunner(self.sic)

        self.user_model = {}
        self.recognition_manager = {'attempt_success': False, 'attempt_number': 0}

    def run(self) -> None:
        self.sic.start()

        self.action_runner.load_waiting_action('set_language', 'en-US')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()
        self.action_runner.run_waiting_action('set_breathing', enable = True)
        self.action_runner.run_waiting_action('say_animated', 'Hey there, I\'m Nao, your favourite silicon friend! What would you like to talk about?')
        while True:
            print(self.__CONVERSATION)
            if TEXT:
                t = input('\nHuman: ')
                self.__CONVERSATION = add_to_conv(self.__CONVERSATION, t, human=True)
                
            else:
                self.action_runner.run_waiting_action('record_audio', 5,
                                                  additional_callback=self.on_intent)
            response = openai.Completion.create(
                engine="davinci",
                prompt=self.__CONVERSATION,
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stop=["\n", " Human:", " Nao:"]
                #stop=['*']
                )
            print(response)
            response_text = response['choices'][0]['text']
            self.action_runner.run_waiting_action('say_animated', response_text)
            self.__CONVERSATION = add_to_conv(self.__CONVERSATION,response_text, human=False)


    def on_intent(self, detection_result) -> None:
        r = sr.Recognizer()
        with sr.AudioFile(detection_result) as source:
            audio_text = r.listen(source)
        text = r.recognize_google(audio_text)
        os.remove(detection_result)

        if text:
            self.__CONVERSATION = add_to_conv(self.__CONVERSATION, text, human=True)
            self.user_model['text'] = text
            self.recognition_manager['attempt_success'] = True
            get_action(text)
        else:
            self.recognition_manager['attempt_number'] += 1

    def reset_recognition_management(self) -> None:
        self.recognition_manager.update({'attempt_success': False, 'attempt_number': 0})

    



example = Example('127.0.0.1',
                  'sir-12-test-jsga-23d5d4c80b77.json',
                  'sir-12-test-jsga')
example.run()