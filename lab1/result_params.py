
class RunResults:
    def __init__(self):
        self.queue_size = 0

        # Make num_looks float for floating point division
        self.num_looks = 0.0

        self.queue_delay = 0
        self.server_idle_time = 0
        self.queue_empty_tick = 0
        self.dep_tick = 0
