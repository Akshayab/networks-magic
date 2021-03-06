# Authors: Akshay Budhkar and Ashwin Raman
# Submission for ECE 358 Lab 1

from Queue import Queue
from math import log, ceil

from result_params import RunResults
from matplotlib import pyplot as plt

import random
import argparse
import logging
import sys
import numpy as np


def generate_packet(arrival_tick):
    packet = {}
    packet['arrival_tick'] = arrival_tick

    return packet


# Handles arrival of a new packet
def arrival(packet_queue, cur_tick, run_results, sim_params):
    # If finite queue and the queue is full, drop the packet
    if packet_queue.maxsize > 0:
        if packet_queue.qsize() == packet_queue.maxsize:
            run_results.packet_loss += 1
            return

    if packet_queue.qsize() == 0:
        run_results.server_idle_time += (cur_tick - run_results.queue_empty_tick)
        run_results.dep_tick = cur_tick + calc_next_departure_time(sim_params)

    new_packet = generate_packet(cur_tick)
    packet_queue.put(new_packet)

    logger.debug("Packet arrived.")


# Handles departure of the latest packet in the buffer
def departure(packet_queue, cur_tick, run_results, sim_params):
    # Calculate the packet queue size
    run_results.queue_size += packet_queue.qsize()
    run_results.num_looks += 1

    # Calculate queue delay
    packet = packet_queue.get()
    # Queue delay = departure time - arrival time - service time
    run_results.queue_delay += cur_tick - (packet['arrival_tick']) - calc_next_departure_time(sim_params)
    run_results.sojourn_time += cur_tick - (packet['arrival_tick'])

    logger.debug("Packet departed.")

    # Record tick if queue is empty and set the next departure time to be Inf (total ticks + 1)
    if packet_queue.qsize() == 0:
        run_results.queue_empty_tick = cur_tick
        run_results.dep_tick = sim_params.ticks + 1
    else:
        run_results.dep_tick = cur_tick + calc_next_departure_time(sim_params)


# Time taken to process a packet
def calc_next_departure_time(sim_params):
    return (sim_params.packet_size / float(sim_params.transmission_rate)) * sim_params.tick_length


# Random generator used to calculate the tick when the next packet will be generated
def calc_next_arrival_time(sim_params):
    u = random.uniform(0, 1)  # generate random number between 0...1
    arrival_time = (-1.0/sim_params.l) * log((1-u)) * sim_params.tick_length

    logger.debug("Next arrival time = " + str(arrival_time))
    return arrival_time


def create_report_inf(queue_size, queue_delay, idle_time, average_sojourn_time, rho):

    logger.info("Average queue size: ")
    logger.info(queue_size)
    logger.info("Queue delay: ")
    logger.info(queue_delay)
    logger.info("Idle Time: ")
    logger.info(idle_time)
    logger.info("Rho: ")
    logger.info(rho)

    plt.figure(1)
    plt.plot(rho, queue_size)
    plt.xlabel('Rho')
    plt.ylabel('Queue Size')

    plt.figure(2)
    plt.plot(rho, queue_delay)
    plt.xlabel('Rho')
    plt.ylabel('Queue Delay')

    plt.figure(3)
    plt.plot(rho, idle_time)
    plt.xlabel('Rho')
    plt.ylabel('Idle Time')

    plt.figure(4)
    plt.plot(rho, average_sojourn_time)
    plt.xlabel('Rho')
    plt.ylabel('Average Sojourn Time')

    plt.show()


def create_report_fin(queue_size, queue_delay, idle_time, average_sojourn_time, packet_loss, rho):

    logger.info("Average queue size: ")
    logger.info(queue_size)
    logger.info("Queue delay: ")
    logger.info(queue_delay)
    logger.info("Idle Time: ")
    logger.info(idle_time)
    logger.info("Packet Loss: ")
    logger.info(packet_loss)
    logger.info("Rho: ")
    logger.info(rho)

    labels = ['M/D/10', 'M/D/25', 'M/D/50']

    print np.shape(rho)
    print np.shape(queue_delay)
    print np.shape(packet_loss)

    plt.figure(1)
    for i in range(3):
        plt.plot(rho[i], queue_size[i], label=labels[i], alpha=0.5)

    plt.xlabel('Rho')
    plt.ylabel('Queue Size')
    plt.legend(loc='upper right')

    plt.figure(2)
    for i in range(3):
        plt.plot(rho[i], queue_delay[i], label=labels[i], alpha=0.5)

    plt.xlabel('Rho')
    plt.ylabel('Queue Delay')
    plt.legend(loc='upper right')

    plt.figure(3)
    for i in range(3):
        plt.plot(rho[i], idle_time[i], label=labels[i], alpha=0.5)

    plt.xlabel('Rho')
    plt.ylabel('Idle Time')
    plt.legend(loc='upper right')

    plt.figure(4)
    for i in range(3):
        plt.plot(rho[i], average_sojourn_time[i], label=labels[i], alpha=0.5)

    plt.xlabel('Rho')
    plt.ylabel('Average Sojourn Time')
    plt.legend(loc='upper right')

    # For an M/D/K buffer
    plt.figure(5)
    for i in range(3):
        plt.plot(rho[i], packet_loss[i], label=labels[i], alpha=0.5)

    plt.xlabel('Rho')
    plt.ylabel('Packet Loss')
    plt.legend(loc='upper right')

    plt.show()


def simulate(sim_params, max_size, average_queue_size, average_queue_delay, prop_idle_time, average_sojourn_time,
             packet_loss, rho):
    for i in range(sim_params.num_runs):
        logger.info("Run " + str(i + 1) + "/" + str(sim_params.num_runs) + ": ")
        logger.info("Setting random number seed to " + str(i))
        random.seed(i)

        packet_queue = Queue()

        # Set this if an M/D/K buffer
        packet_queue.maxsize = max_size

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

        if run_results.num_looks == 0:
            logger.warn("Simulation was too short to simulate departure")

        # Save run results after each run for plotting at the end
        average_queue_size.append(run_results.queue_size / run_results.num_looks)
        average_queue_delay.append(run_results.queue_delay / run_results.num_looks)
        prop_idle_time.append(run_results.server_idle_time / float(sim_params.ticks))
        average_sojourn_time.append(run_results.sojourn_time / run_results.num_looks)
        packet_loss.append(run_results.packet_loss / run_results.num_looks)

        # Calculate and save rho to plot values, saved above, against
        current_rho = (sim_params.l * sim_params.packet_size) / float(sim_params.transmission_rate)
        rho.append(current_rho)


def finite_queue_simulation(sim_params):
    all_queue_sizes = []
    all_queue_delays = []
    all_idle_times = []
    all_sojourn_times = []
    all_packet_losses = []
    all_rhos = []

    max_sizes = [10, 25, 50]

    for max_size in max_sizes:
        average_queue_size = []
        average_queue_delay = []
        prop_idle_time = []
        average_sojourn_time = []
        packet_loss = []
        rho = []

        for sim_params.l in range(250, 750, 50):
            simulate(sim_params, max_size, average_queue_size, average_queue_delay, prop_idle_time,
                     average_sojourn_time, packet_loss, rho)

        all_queue_sizes.append(average_queue_size)
        all_queue_delays.append(average_queue_delay)
        all_idle_times.append(prop_idle_time)
        all_sojourn_times.append(average_sojourn_time)
        all_packet_losses.append(packet_loss)
        all_rhos.append(rho)

    create_report_fin(all_queue_sizes, all_queue_delays, all_idle_times, all_sojourn_times, all_packet_losses, all_rhos)


def infinite_queue_simulation(sim_params):
    average_queue_size = []
    average_queue_delay = []
    prop_idle_time = []
    average_sojourn_time = []
    packet_loss = []
    rho = []

    max_size = 0

    for sim_params.l in range(50, 500, 50):
        simulate(sim_params, max_size, average_queue_size, average_queue_delay, prop_idle_time,
                 average_sojourn_time, packet_loss, rho)

    create_report_inf(average_queue_size, average_queue_delay, prop_idle_time, average_sojourn_time, rho)


def custom_simulation(sim_params):
    average_queue_size = []
    average_queue_delay = []
    prop_idle_time = []
    average_sojourn_time = []
    packet_loss = []
    rho = []

    simulate(sim_params, sim_params.max_size, average_queue_size, average_queue_delay, prop_idle_time,
             average_sojourn_time, packet_loss, rho)

    logger.info("Average queue size: ")
    logger.info(average_queue_size)
    logger.info("Queue delay: ")
    logger.info(average_queue_delay)
    logger.info("Idle Time: ")
    logger.info(prop_idle_time)
    logger.info("Average Packet Loss: ")
    logger.info(packet_loss)
    logger.info("Average Sojourn Time: ")
    logger.info(average_sojourn_time)
    logger.info("Rho: ")
    logger.info(rho)


def main(sim_params):
    logger.debug(sim_params)

    if sim_params.custom_sim:
        custom_simulation(sim_params)
    else:
        if sim_params.finite_queue:
            finite_queue_simulation(sim_params)
        else:
            infinite_queue_simulation(sim_params)

    # create_report(average_queue_size, average_queue_delay, prop_idle_time, average_sojourn_time, packet_loss, rho)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulates a network queue based on the given parameters.')
    parser.add_argument('-l', type=int, default=100)
    parser.add_argument('--tick-length', type=int, default=500000, help="1 sec = ? ticks")
    parser.add_argument('--ticks', type=int, default=2000000)
    parser.add_argument('--packet-size', type=int, default=2000)
    parser.add_argument('--transmission-rate', type=int, default=1000000)
    parser.add_argument('--num-runs', type=int, default=5)
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('--finite_queue', action="store_true")
    parser.add_argument('--max_size', default=0, help="Set this var less than or equal to zero for infinite size queue")
    parser.add_argument('--custom_sim', action="store_true")

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
    sim_params.ticks += 1

    main(sim_params)
