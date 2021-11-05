from time import sleep
import random

from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector
import json
import pickle

class Example:

    def __init__(self, server_ip: str):
        self.sic = BasicSICConnector(server_ip)
        self.action_runner = ActionRunner(self.sic)
        self.motion = None

    def run(self) -> None:
        self.sic.start()

        joints = ['RArm']
        self.action_runner.load_waiting_action('set_language', 'en-US')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()

        self.action_runner.run_waiting_action('set_stiffness', joints, 0)
        self.action_runner.load_waiting_action('say', 'Move right arm please')
        self.action_runner.load_waiting_action('start_record_motion', joints)
        self.action_runner.run_loaded_actions()
        sleep(5)
        self.action_runner.load_waiting_action('stop_record_motion', additional_callback=self.retrieve_recorded_motion)
        self.action_runner.load_waiting_action('say', 'Done')
        self.action_runner.run_loaded_actions()

        # self.action_runner.run_waiting_action('set_stiffness', joints, 100)
        # if self.motion:
        #     self.action_runner.run_waiting_action('say', 'I will now replay your movement')
        #     self.action_runner.run_waiting_action('play_motion', self.motion)
        # else:
        #     self.action_runner.run_waiting_action('say', 'Something went wrong.')

        #self.action_runner.run_waiting_action('rest')

        # motions = None
        # try:
        #     with open('motions.json','rb') as infile:
        #         motions = pickle.load(infile)
        #     print(motions)
        # except EOFError as e:
        #     print(e, ':(')
        # for motion in motions:
        #     self.action_runner._waiting_action('play_motion', motions[motion])

        # self.action_runner.run_loaded_actions()


        self.sic.stop()

    def retrieve_recorded_motion(self, motion) -> None:
        self.motion = motion





example = Example('127.0.0.1')
example.run()
print(type(example.motion))

motions = None
try:
    with open('motions.json','rb') as infile:
        motions = pickle.load(infile)
        print(motions)
except EOFError as e:
    print(e, ':(')

for motion in motions:
    example.action_runner.load_waiting_action('play_motion', motions[motion])
example.action_runner.run_loaded_actions()


# if motions:
#     motions[f'Action{random.randint(2, 1000)}'] = example.motion
# else:
#     motions = {'Action1' : example.motion}

# with open('motions.json', 'wb') as outfile:
#     pickle.dump(motions, outfile)




