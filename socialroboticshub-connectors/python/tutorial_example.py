from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector, RobotPosture

class MyFirstApplication:
    def __init__(self, ip:str):
        self.sic = BasicSICConnector(server_ip=ip)
        self.runner = ActionRunner(self.sic)

        self.go_to_crouch_runner = ActionRunner(self.sic)
        self.go_to_crouch_runner.load_action("say", 'I am going to crouch now.')
        self.go_to_crouch_runner.load_action('go_to_posture', RobotPosture.CROUCH)

        self.go_to_stand_runner = ActionRunner(self.sic)
        self.go_to_stand_runner.load_action("say", 'I am going to stand now.')
        self.go_to_stand_runner.load_action('go_to_posture', RobotPosture.STAND)
        self.go_to_stand_runner.run_loaded_actions()

    def run(self) -> None:
        self.sic.start()
        
        self.runner.run_waiting_action("set_language", 'en-US')
        self.runner.run_waiting_action("say", "Hello world!")

        self.runner.run_waiting_action('wake_up')

        self.runner.run_touch_listener(touch_event='MiddleTactilTouched', callback=self.change_posture, continuous=True)
        self.runner.run_touch_listener(touch_event='RearTactilTouched', callback=self.wrap_up, continuous=True)


    def change_posture(self):
        if self.sic.robot_state["posture"] == RobotPosture.CROUCH:
            self.go_to_crouch_runner.run_loaded_actions(clear=False)
        elif self.sic.robot_state["posture"] == RobotPosture.STAND:
            self.go_to_stand_runner.run_loaded_actions(clear=False)

    def wrap_up(self):
        self.runner.run_action('rest')
        self.sic.stop()

my_first_application = MyFirstApplication('127.0.0.1')
my_first_application.run()