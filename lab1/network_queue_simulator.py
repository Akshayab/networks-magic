from Queue import Queue
from math import log, ceil

from result_params import RunResults
from matplotlib import pyplot as plt

import random
import argparse
import logging
import sys


def generate_packet(arrival_tick):
    packet = {}
    packet['arrival_tick'] = arrival_tick

    return packet


# Handles arrival of a new packet
def arrival(packet_queue, cur_tick, run_results, sim_params):

    if packet_queue.qsize() == 0:
        run_results.server_idle_time += (cur_tick - run_results.queue_empty_tick)
        run_results.dep_tick = cur_tick + calc_next_departure_time(sim_params)

    new_packet = generate_packet(cur_tick)
    packet_queue.put(new_packet)

    logger.debug("Packet arrived.")
    # Also need to consider packet loss case when queue is full


# Handles departure of the latest packet in the buffer
def departure(packet_queue, cur_tick, run_results, sim_params):
    # Calculate the packet queue size
    run_results.queue_size += packet_queue.qsize()
    run_results.num_looks += 1

    # Calculate queue delay
    packet = packet_queue.get()
    # Queue delay = departure time - arrival time - service time
    run_results.queue_delay += cur_tick - (packet['arrival_tick']) - calc_next_departure_time(sim_params)

    logger.debug("Packet departed.")

    # Record tick if queue is empty and set the next departure time to be Inf (total ticks + 1)
    if packet_queue.qsize() == 0:
        run_results.queue_empty_tick = cur_tick
        run_results.dep_tick = sim_params.ticks + 1
    else:
        run_results.dep_tick = cur_tick + calc_next_departure_time(sim_params)


# Time taken to process a packet
def calc_next_departure_time(sim_params):
    return sim_params.packet_size / sim_params.transmission_rate


# Random generator used to calculate the tick when the next packet will be generated
def calc_next_arrival_time(sim_params):
    u = random.uniform(0, 1)  # generate random number between 0...1
    arrival_time = (-1.0/sim_params.l) * log((1-u)) * sim_params.tick_length

    logger.debug("Next arrival time = " + str(arrival_time))
    return arrival_time


# TODO: Generate report
def create_report(queue_size, queue_delay, idle_time, rho):

    print(queue_size, queue_delay, idle_time, rho)

    plt.plot(rho, queue_size)
    plt.xlabel('Rho')
    plt.ylabel('Queue Size')

    plt.plot(rho, queue_delay)
    plt.xlabel('Rho')
    plt.ylabel('Queue Delay')

    plt.plot(rho, idle_time)
    plt.xlabel('Rho')
    plt.ylabel('Idle Time')

    plt.show()


def main(sim_params):
    logger.debug(sim_params)

    average_queue_size = []
    average_queue_delay = []
    prop_idle_time = []

    rho = []

    for i in range(sim_params.num_runs):
        logger.info("Run " + str(i+1) + "/" + str(sim_params.num_runs) + ": ")
        logger.info("Setting random number seed to " + str(i))
        random.seed(i)
        packet_queue = Queue()

        # Calculating rho
        sim_params.rho = sim_params.l * (sim_params.packet_size / sim_params.transmission_rate)

        arrival_tick = int(calc_next_arrival_time(sim_params))  # calculate first packet arrival time
        dep_tick = sim_params.ticks + 1  # Departure only occurs after the first arrival
        logger.info("First arrival_tick = " + str(arrival_tick))
        logger.info("First departure tick = " + str(dep_tick))

        # Initialize simulation results to zero for computing average
        run_results = RunResults()
        run_results.dep_tick = sim_params.ticks + 1

        for cur_tick in range(1, sim_params.ticks):
            if cur_tick == ceil(arrival_tick):
                arrival(packet_queue, cur_tick, run_results, sim_params)

                arrival_tick = cur_tick + calc_next_arrival_time(sim_params)

            if cur_tick == ceil(run_results.dep_tick):
                departure(packet_queue, cur_tick, run_results, sim_params)

        run_results.server_idle_time += (sim_params.ticks - run_results.queue_empty_tick)

        # Save run results after each run for plotting at the end
        average_queue_size.append(run_results.queue_size / run_results.num_looks)
        average_queue_delay.append(run_results.queue_delay / run_results.num_looks)
        prop_idle_time.append(run_results.server_idle_time / sim_params.ticks)

        # Calculate and save rho to plot values, saved above, against
        current_rho = (sim_params.l * sim_params.packet_size)/float(sim_params.transmission_rate)
        rho.append(current_rho)

        # Modify input rate for the next run
        sim_params.l += 50

    create_report(average_queue_size, average_queue_delay, prop_idle_time, rho)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulates a network queue based on the given parameters.')
    parser.add_argument('-l', type=int, default=100)
    parser.add_argument('--tick-length', type=int, default=500000, help="1 sec = ? ticks")
    parser.add_argument('--ticks', type=int, default=10000)
    parser.add_argument('--packet-size', type=int, default=2000)
    parser.add_argument('--transmission-rate', type=int, default=1000000)
    parser.add_argument('--num-runs', type=int, default=5)
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

    # Time = Infinity is set as sim_params.ticks + 1.
    sim_params.ticks += 2

    main(sim_params)
