from Queue import Queue

class Hub:
    def __init__(self):
        self.hub_packet_queue = Queue()
        self.has_collided = False
        self.collision_end_tick = 0

    def update_collision(self, tick):
        self.has_collided = True
        while not self.hub_packet_queue.empty():
            self.hub_packet_queue.get()
