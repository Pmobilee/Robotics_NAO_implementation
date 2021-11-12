import openai
import speech_recognition as sr
import os
import threading
import time

TEXT = False
openai.api_key = os.getenv('GPT3_KEY')

def add_to_conv(C, text, human = True):
    if human:
        C += f"\nHuman: {text}\nNao: "
    else:
        C += f"{text}"
    return C

response = 'default '
print(response)

# Get human input

from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector


class Example:
    """Example that uses speech recognition. Prerequisites are the availability of a dialogflow_key_file,
    a dialogflow_agent_id, and a running Dialogflow service. For help meeting these Prerequisites see
    https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/260276225/The+Social+Interaction+Cloud+Manual"""

    standby = False
    taps = 0
    __CONVERSATION = "The following is a conversation with a personal assistant called Nao. Nao is a child prodigy who is now 25, he is an expert in music..\n\nNao: Hi I am Nao. I am an expert about music theory and the culture surrounding it."

    def __init__(self, server_ip: str, dialogflow_key_file: str, dialogflow_agent_id: str):
        self.sic = BasicSICConnector(server_ip, 'en-US', dialogflow_key_file, dialogflow_agent_id)
        self.action_runner = ActionRunner(self.sic)

        self.action_runner_openai = ActionRunner(self.sic)
        self.action_runner_openai.load_action('say_animated', 'I am listening.')

        self.action_runner_standby = ActionRunner(self.sic)
        self.action_runner_standby.load_action('say_animated', 'I am sleeping.')

        self.user_model = {}
        self.recognition_manager = {'attempt_success': False, 'attempt_number': 0}
        self.awake_lock = threading.Event()
        
    
    #def head_tapped_sleep(self):
        #self.sic.unsubscribe_touch_listener('MiddleTactilTouched')
        #self.taps += 1
        #self.standby = True
        #self.sic.subscribe_touch_listener('RightBumperPressed', self.head_tapped_awake)

    #def head_tapped_awake(self):
        #self.taps += 1
        #self.standby = False
        #self.sic.subscribe_touch_listener('MiddleTactilTouched', self.head_tapped_sleep)
        #self.sic.unsubscribe_touch_listener('RightBumperPressed')

    def awake(self):
        self.awake_lock.set()

    def run(self) -> None:
        self.sic.start()

        self.action_runner.load_waiting_action('set_language', 'en-US')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()

        self.sic.wake_up(self.awake)
        self.awake_lock.wait()
        
        self.sic.subscribe_touch_listener('MiddleTactilTouched', self.change_state)

        self.action_runner.run_waiting_action('say_animated', 'Hi I am Nao. I am an expert about music theory and the culture surrounding it.')
        
        while True:
            while not self.standby:
                
                print(self.__CONVERSATION)
                if TEXT:
                    t = input('\nHuman: ')
                    self.__CONVERSATION = add_to_conv(self.__CONVERSATION, t, human=True)
                    
                else:
                    
                    self.action_runner_openai.run_waiting_action('record_audio', 5,
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

                self.action_runner_openai.run_waiting_action('say_animated', response_text)
                self.__CONVERSATION = add_to_conv(self.__CONVERSATION,response_text, human=False)

    def change_state(self):
        if self.standby == True:
            self.action_runner_openai.run_loaded_actions(clear=False)
        else:
            self.action_runner_standby.run_loaded_actions(clear=False)
        self.standby = not self.standby

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
        else:
            self.recognition_manager['attempt_number'] += 1

    def reset_recognition_management(self) -> None:
        self.recognition_manager.update({'attempt_success': False, 'attempt_number': 0})


example = Example('127.0.0.1',
                  'sir-12-test-jsga-23d5d4c80b77.json',
                  'sir-12-test-jsga')
example.run()