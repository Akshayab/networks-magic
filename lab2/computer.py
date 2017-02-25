import random

from Queue import Queue
from math import log, ceil


class Computer:
    def __init__(self, logger):
        self.next_event_tick = 0
        self.logger = logger

    def generate_packet(self, arrival_tick):
        packet = {}
        packet['arrival_tick'] = arrival_tick

        return packet

    # Handles arrival of a new packet
    def arrival(self, packet_queue, cur_tick, run_results, sim_params):
        # If finite queue and the queue is full, drop the packet
        if packet_queue.maxsize > 0:
            if packet_queue.qsize() == packet_queue.maxsize:
                run_results.packet_loss += 1
                return

        if packet_queue.qsize() == 0:
            run_results.server_idle_time += (cur_tick - run_results.queue_empty_tick)
            run_results.dep_tick = cur_tick + self.calc_next_departure_time(sim_params)

        new_packet = self.generate_packet(cur_tick)
        packet_queue.put(new_packet)

        self.logger.debug("Packet arrived.")

    # Handles departure of the latest packet in the buffer
    def departure(self, packet_queue, cur_tick, run_results, sim_params):
        # Calculate the packet queue size
        run_results.queue_size += packet_queue.qsize()
        run_results.num_looks += 1

        # Calculate queue delay
        packet = packet_queue.get()
        # Queue delay = departure time - arrival time - service time
        run_results.queue_delay += cur_tick - (packet['arrival_tick']) - self.calc_next_departure_time(sim_params)
        run_results.sojourn_time += cur_tick - (packet['arrival_tick'])

        logger.debug("Packet departed.")

        # Record tick if queue is empty and set the next departure time to be Inf (total ticks + 1)
        if packet_queue.qsize() == 0:
            run_results.queue_empty_tick = cur_tick
            run_results.dep_tick = sim_params.ticks + 1
        else:
            run_results.dep_tick = cur_tick + self.calc_next_departure_time(sim_params)

    # Time taken to process a packet
    def calc_next_departure_time(self, sim_params):
        return (sim_params.packet_size / float(sim_params.transmission_rate)) * sim_params.tick_length

    # Random generator used to calculate the tick when the next packet will be generated
    def calc_next_arrival_time(self, sim_params):
        u = random.uniform(0, 1)  # generate random number between 0...1
        arrival_time = (-1.0 / sim_params.l) * log((1 - u)) * sim_params.tick_length

        self.logger.debug("Next arrival time = " + str(arrival_time))
        return arrival_time