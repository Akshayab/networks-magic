import logging
import argparse
import sys

from result_params import RunResults
from hub import Hub
from computer import Computer


def simulate(sim_params, logger):
    stations = []
    hub = Hub(logger)

    hub.stations = stations

    run_results = RunResults()

    for i in range(sim_params.N):
        stations.append(Computer(logger, sim_params, hub))

    for tick in range(sim_params.ticks):
        for station in stations:
            if station.next_arrival_tick == tick:
                station.arrival(tick, run_results)
                logger.debug("Tick " + str(tick))

            if station.next_event_tick == tick:
                logger.debug("Tick " + str(tick))
                station.fsm.next()

            if station.depart_packet:
                station.departure(tick, run_results)


def main(parser):
    sim_params = parser.parse_args()
    sim_params.finite_queue = False

    # 1 tick = 10 us (given in ppt)
    sim_params.tick_length = 100000

    # packet size = 1 byte
    sim_params.packet_size = 1000 * 8

    # transmission rate = 1 Mbps
    sim_params.transmission_rate = 1000000

    sim_params.ticks = 100000

    logging.info("Begin")
    logger = logging.getLogger(__name__)
    sh = logging.StreamHandler(sys.stdout)

    if sim_params.debug:
        sh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        sh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    logger.debug(sim_params)

    simulate(sim_params, logger)

    # create_report(average_queue_size, average_queue_delay, prop_idle_time, average_sojourn_time, packet_loss, rho)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulates a network queue based on the given parameters.')
    parser.add_argument('-N', type=int, default=16)
    parser.add_argument('-A', type=int, default=16)
    #parser.add_argument('--ticks', type=int, default=2000000)
    #parser.add_argument('--num-runs', type=int, default=5)
    parser.add_argument('--debug', action="store_true")

    main(parser)
