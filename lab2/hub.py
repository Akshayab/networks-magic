from Queue import Queue

class Hub:
    def __init__(self, logger):
        self.hub_packet_queue = Queue()
        self.has_collided = False
        self.collision_end_tick = 0

        self.num_collisions = 0
        self.stations = []
        self.logger = logger

        self.num_packets_trans = 0

    def update_collision(self):
        self.has_collided = True
        self.num_collisions += 1
        while not self.hub_packet_queue.empty():
            self.hub_packet_queue.get()

    def transmit(self):
        if self.hub_packet_queue.empty():
            self.logger.error("Hub queue empty - transmit called")
            return False

        packet = self.hub_packet_queue.get()
        for station in self.stations:
            station.t1_queue.put(packet)

        return self.check_last_stage_collision()

    # Assumption: The sender cannot receive any other packet because the packets would have collided
    # sooner than the receive_queue of the sender. So it is okay to send back to the sender.
    def check_last_stage_collision(self):
        collided = False
        for station in self.stations:
            if station.t1_queue.qsize() > 1:
                collided = True
                self.num_collisions += 1

        return not collided

    def complete_transmission(self):
        self.logger.debug("Completing transmission")
        self.num_packets_trans += 1
        for station in self.stations:
            if not station.t1_queue.empty():
                station.t1_queue.get()
