from time import sleep
from social_interaction_cloud.abstract_connector import AbstractSICConnector
from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector, RobotPosture


class MyConnector(AbstractSICConnector):

    def __init__(self, server_ip: str, dialogflow_key_file: str, dialogflow_agent_id: str):
        super(MyConnector, self).__init__(server_ip)
        self.sic = BasicSICConnector(server_ip, dialogflow_key_file, dialogflow_agent_id)

    def run(self) -> None:
        self.start()

        action_runner = ActionRunner(self.sic)
        action_runner.run_waiting_action('wake_up')
        action_runner.run_waiting_action('set_language', 'en-US')
        sleep(1)  # wait for the language to change
        self.say('Hello, Group 12! My name is Hal')
        sleep(3)  # wait for the robot to be done speaking (to see the relevant prints)
        action_runner.load_waiting_action('say', 'I\'m going to crouch now.')
        action_runner.load_waiting_action('go_to_posture', RobotPosture.CROUCH,
                                          additional_callback=self.posture_callback)
        action_runner.run_loaded_actions()
        action_runner.load_waiting_action('say', 'I\'m going to stand now.')
        action_runner.load_waiting_action('go_to_posture', RobotPosture.STAND,
                                          additional_callback=self.posture_callback)
        action_runner.run_loaded_actions()
        action_runner.run_waiting_action('rest')

        self.stop()

    def on_robot_event(self, event: str) -> None:
        print(event)


# Run the application
my_connector = MyConnector('127.0.0.1',
                  'sir-12-test-jsga-23d5d4c80b77.json',
                  'sir-12-test-jsga')
my_connector.run()
