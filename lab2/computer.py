import random

from Queue import Queue
from math import log, pow, ceil


class Computer:
    def __init__(self, logger, sim_params, hub):
        self.next_event_tick = -1
        self.next_arrival_tick = 0

        self.hub = hub
        self.depart_packet = False

        self.packet_queue = Queue()

        self.logger = logger
        self.sim_params = sim_params

        self.i = 0
        self.packet_generator()
        self.fsm = self.csma_cd()

    def generate_packet(self, arrival_tick):
        packet = {}
        packet['arrival_tick'] = arrival_tick

        return packet

    def packet_generator(self):
        self.next_arrival_tick += self.calc_next_arrival_time(self.sim_params)

    def csma_cd(self):
        while(True):
            prop_length = 3
            self.next_event_tick += 960
            self.logger.debug("Before sensing medium")
            self.logger.debug("Next event tick: " + str(self.next_event_tick))
            yield

            j = 0
            while self.medium_busy():
                self.next_event_tick += self.bin_exp_back(j)
                self.next_event_tick += 960
                self.logger.debug("Sensing medium")
                self.logger.debug("Next event tick: " + str(self.next_event_tick))
                j += 1
                yield

            self.next_event_tick += prop_length/3
            self.logger.debug("Transmitting - 1")
            self.logger.debug("Next event tick: " + str(self.next_event_tick))
            yield

            # Ignoring Mac level collisions
            self.hub.hub_packet_queue.put(1)

            for i in range(prop_length/3):
                self.logger.debug("Hub Queue Size " + str(self.hub.hub_packet_queue.qsize()))
                if self.hub.hub_packet_queue.qsize() > 1:
                    self.hub.update_collision()
                    break

                self.next_event_tick += 1
                self.logger.debug("Transmitting - 2")
                self.logger.debug("Next event tick: " + str(self.next_event_tick))
                yield

            if self.hub.has_collided:
                self.next_event_tick += (480 + self.bin_exp_back(self.i))
                self.logger.info("Number of collisions: " + str(self.hub.num_collisions))
                self.logger.info("Next event tick: " + str(self.next_event_tick))
                self.i += 1
                continue

            self.hub.hub_packet_queue.get()
            self.next_event_tick += prop_length / 3
            self.logger.debug("Transmitting - 3")
            self.logger.debug("Next event tick: " + str(self.next_event_tick))
            yield

            self.depart_packet = True
            self.i = 0
            yield

    def bin_exp_back(self, i):
        if i > 10:
            raise Exception("i is greater than 10")

        R = random.randint(0, pow(2, i) - 1)
        return R * 5120

    def medium_busy(self):
        return self.hub.has_collided and (self.hub.hub_packet_queue.qsize > 0)

    # Handles arrival of a new packet
    def arrival(self, cur_tick, run_results):
        if self.packet_queue.qsize() == 0:
            self.next_event_tick = cur_tick
            self.logger.debug("Arrival: Next event tick = " + str(self.next_event_tick))
            run_results.dep_tick = cur_tick + self.calc_next_departure_time(self.sim_params)

        new_packet = self.generate_packet(cur_tick)
        self.packet_queue.put(new_packet)

        self.logger.debug("Packet arrived.")
        self.packet_generator()

    # Handles departure of the latest packet in the buffer
    def departure(self, cur_tick, run_results):
        self.depart_packet = False
        # Calculate the packet queue size
        run_results.queue_size += self.packet_queue.qsize()
        run_results.num_looks += 1

        # Calculate queue delay
        packet = self.packet_queue.get()

        self.logger.debug("Packet departed.")

        # Record tick if queue is empty and set the next departure time to be Inf (total ticks + 1)
        if self.packet_queue.qsize() == 0:
            run_results.dep_tick = self.sim_params.ticks + 1
        else:
            run_results.dep_tick = cur_tick + self.calc_next_departure_time(self.sim_params)

    # Time taken to process a packet
    def calc_next_departure_time(self, sim_params):
        return ceil((sim_params.packet_size / float(sim_params.transmission_rate)) * sim_params.tick_length)

    # Random generator used to calculate the tick when the next packet will be generated
    def calc_next_arrival_time(self, sim_params):
        u = random.uniform(0, 1)  # generate random number between 0...1
        arrival_time = (-1.0 / sim_params.A) * log((1 - u)) * sim_params.tick_length

        self.logger.debug("Next arrival time = " + str(arrival_time))
        return ceil(arrival_time)