
from Queue import Queue
from math import log

import random
import argparse
import logging
import sys

def generate_packet():
    packet = "Hello"

    return packet

def arrival(packet_queue):
    # TODO: Determine data structure to represent a packet
    new_packet = generate_packet()
    packet_queue.put(new_packet)

    logger.debug("Packet arrived.")
    # Also need to consider packet loss case when queue is full

def departure(packet_queue):
    packet_queue.get()
    logger.debug("Packet departed.")

def calc_next_departure_time(sim_params):
    return sim_params.packet_size / sim_params.transmission_rate

def calc_next_arrival_time(sim_params):
    u=random.uniform(0,1)  # generate random number between 0...1
    arrival_time= (-1.0/sim_params.l) * log((1-u)) * sim_params.tick_length

    logger.debug("Next arrival time = " + str(arrival_time))
    return arrival_time

# TODO: Generate report
def create_report():
    pass

def main(sim_params):
    logger.debug(sim_params)

    for i in range(sim_params.num_runs):
        logger.info("Run " + str(i+1) + "/" + str(sim_params.num_runs) + ": ")
        logger.info("Setting random number seed to " + str(i))
        random.seed(i)
        packet_queue = Queue()

        arrival_tick = calc_next_arrival_time(sim_params)  # calculate first packet arrival time
        dep_tick = sim_params.ticks + 1  # Departure only occurs after the first arrival
        logger.info("First arrival_tick = " + str(arrival_tick))
        logger.info("First departure tick = " + str(dep_tick))

        for cur_tick in range(sim_params.ticks):
            if cur_tick >= arrival_tick:
                arrival(packet_queue)

                arrival_tick = cur_tick + calc_next_arrival_time(sim_params)
                dep_tick = cur_tick + calc_next_departure_time(sim_params)

            if cur_tick >= dep_tick:
                departure(packet_queue)
                dep_tick = sim_params.ticks + 1

    create_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulates a network queue based on the given parameters.')
    parser.add_argument('-l', type=int, default=200)
    parser.add_argument('--tick-length', type=int, default=500000, help="1 tick = ? sec")
    parser.add_argument('--ticks', type=int, default=10000)
    parser.add_argument('--packet-size', type=int, default=512)
    parser.add_argument('--transmission-rate', type=int, default=512)
    parser.add_argument('--num-runs', type=int, default=1)
    parser.add_argument('--debug', action="store_true")

    sim_params = parser.parse_args()

    logger = logging.getLogger(__name__)
    sh = logging.StreamHandler(sys.stdout)

    if sim_params.debug:
        sh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        sh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    logger.addHandler(sh)

    main(sim_params)