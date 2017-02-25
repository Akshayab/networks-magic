import random

from Queue import Queue
from math import log, ceil


class Computer:
    def __init__(self, logger, sim_params):
        self.next_event_tick = 0
        self.next_arrival_tick = 0

        self.depart_packet = False

        self.packet_queue = Queue()

        self.logger = logger
        self.sim_params = sim_params

    def generate_packet(self, arrival_tick):
        packet = {}
        packet['arrival_tick'] = arrival_tick

        return packet

    def packet_generator(self):
        self.next_arrival_tick = self.calc_next_arrival_time(self.sim_params)


    def csma_cd(self):
        self.next_event_tick += 960
        yield

        while self.medium_busy():
            # self.next_event_tick += self.bin_exp_back()
            self.next_event_tick += 960
            yield

        self.depart_packet = True


    def medium_busy(self):
        pass

    # Handles arrival of a new packet
    def arrival(self, cur_tick, run_results):
        if self.packet_queue.qsize() == 0:
            self.next_event_tick = cur_tick
            run_results.dep_tick = cur_tick + self.calc_next_departure_time(self.sim_params)

        new_packet = self.generate_packet(cur_tick)
        self.packet_queue.put(new_packet)

        self.logger.debug("Packet arrived.")

    # Handles departure of the latest packet in the buffer
    def departure(self, cur_tick, run_results):
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
        return (sim_params.packet_size / float(sim_params.transmission_rate)) * sim_params.tick_length

    # Random generator used to calculate the tick when the next packet will be generated
    def calc_next_arrival_time(self, sim_params):
        u = random.uniform(0, 1)  # generate random number between 0...1
        arrival_time = (-1.0 / sim_params.l) * log((1 - u)) * sim_params.tick_length

        self.logger.debug("Next arrival time = " + str(arrival_time))
        return arrival_time