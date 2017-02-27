#########################
# Authors: Akshay Budhkar and Ashwin Raman
# Submission for Lab 2 of ECE 358/
# Simulates behavior of every computer station.
# Implements CSMA/CD protocol and handles collisions at a lower level.
# Responsible for packet generation and departure
#########################

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
        self.t1_queue = Queue()

        self.delays = []
        self.current_delay = 0

    def generate_packet(self, arrival_tick):
        packet = {}
        packet['arrival_tick'] = arrival_tick

        return packet

    def packet_generator(self):
        self.next_arrival_tick += self.calc_next_arrival_time(self.sim_params)

    def csma_cd(self):
        while True:
            self.current_delay = self.next_event_tick

            prop_length = 9

            # Assumption: Sensing medium takes 1 tick as mentioned in the PPT and not 96 us as mentioned in the
            # state diagram
            self.next_event_tick += 1
            self.logger.debug("Before sensing medium")
            self.logger.debug("Next event tick: " + str(self.next_event_tick))
            yield

            j = 0
            self.logger.debug("medium busy = " + str(self.medium_busy()))
            while self.medium_busy():
                # For non-persistent protocol
                # self.next_event_tick += self.bin_exp_back(j)

                self.next_event_tick += 1
                self.logger.debug("Sensing medium")
                self.logger.debug("Next event tick: " + str(self.next_event_tick))
                j += 1
                self.logger.debug("medium busy = " + str(self.medium_busy()))
                yield

            self.logger.debug("Transmitting - 1")
            self.t1_queue.put(1)

            local_collision = False
            for i in range(prop_length/3):
                self.next_event_tick += 1
                self.logger.debug("Next event tick: " + str(self.next_event_tick))
                if i == (prop_length / 3) - 1:
                    if self.hub.hub_packet_queue.qsize() > 0:
                        self.logger.info("T1 - updating collision")
                        self.hub.update_collision()
                        local_collision = True
                        break
                yield

                # Mac level collisions
                if self.t1_queue.qsize() > 1:
                    local_collision = True
                    break

            if local_collision:
                self.logger.info("T1 collision")
                self.collision_handler()
                yield
                continue

            self.hub.hub_packet_queue.put(self.t1_queue.get())
            self.logger.debug("T1 queue size : " + str(self.t1_queue.qsize()))

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
                self.hub.has_collided = False
                self.logger.info("T2 collision - 2nd collider")
                self.collision_handler()
                yield
                continue

            if self.hub.hub_packet_queue.empty():
                self.logger.info("T2 collision - 1st collider")
                self.collision_handler()
                yield
                continue

            self.logger.debug("Transmitting - 3")
            if self.hub.transmit():
                self.next_event_tick += 1
                self.logger.debug("Next event tick: " + str(self.next_event_tick))
                yield

                local_collision = False
                for i in range((prop_length/3) - 1):
                    if not self.hub.check_last_stage_collision():
                        local_collision = True
                        break

                    self.next_event_tick += 1
                    self.logger.debug("Transmitting - 3")
                    self.logger.debug("Next event tick: " + str(self.next_event_tick))
                    yield

                if local_collision:
                    self.logger.info("T3 collision - intermediate fail")
                    self.collision_handler()
                    yield
                    continue
            else:
                self.logger.info("T3 collision - Transmit failed")
                self.collision_handler()
                yield
                continue

            self.hub.complete_transmission()
            self.depart_packet = True
            self.delays.append(self.next_event_tick - self.current_delay)
            self.i = 0
            yield

    def calc_avg_delay(self):
        return sum(self.delays)/len(self.delays)

    def collision_handler(self):
        while self.t1_queue.qsize() > 0:
            self.t1_queue.get()

        self.logger.info("Current event tick: " + str(self.next_event_tick))
        self.next_event_tick += (5 + self.bin_exp_back(self.i))
        self.logger.info("Number of collisions: " + str(self.hub.num_collisions))
        self.i += 1

    def bin_exp_back(self, i):
        if i > 10:
            raise Exception("i is greater than 10")

        R = random.randint(0, pow(2, i) - 1)
        return R * 51

    def medium_busy(self):
        return self.hub.has_collided or (self.hub.hub_packet_queue.qsize() > 0) or (self.t1_queue.qsize() > 0)

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
        self.packet_queue.get()

        self.logger.info("Packet departed.")

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
