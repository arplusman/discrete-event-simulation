from random import random, choice, shuffle
from math import exp
from enum import Enum
import heapq


class Process:
    priorities_probability = [0.1, 1]
    id_counter = 0

    def __init__(self, arrival_time):
        self.id = Process.id_counter
        Process.id_counter += 1
        self.arrival_time = arrival_time
        self.reneged = False
        random_value = random()
        for i in range(len(self.priorities_probability)):
            if random_value <= self.priorities_probability[i]:
                self.priority = i
                break


class Processor:
    core_numbers = 3

    def __init__(self, parameters):
        self.cores = [Core(parameters[i], self) for i in range(Processor.core_numbers)]
        self.queue = [[] for _ in range(2)]
        self.queue_length_sum = 0
        self.previous_time = 0


class Core:
    def __init__(self, service_time_parameter, processor):
        self.is_busy = False
        self.total_busy_time = 0
        self.service_time_parameter = service_time_parameter
        self.processor = processor


class Scheduler:
    def __init__(self, mu):
        self.mu = mu
        self.queue = [
            [],
            [],
        ]
        self.is_busy = False
        self.queue_length_sum = 0
        self.previous_time = 0


class Event:
    def __init__(self, event_type, time, process):
        self.time = time
        self.type = event_type
        self.process = process
        self.valid = True

    def __eq__(self, other):
        if self.time == other.time and self.type == other.type:
            return True
        return False

    def __lt__(self, other):
        if self.time < other.time or self.time == other.time and self.type < other.type:
            return True
        return False

    def __gt__(self, other):
        if self.time > other.time or self.time == other.time and self.type > other.type:
            return True
        return False


class EventType(Enum):
    Departure = 1
    FindProcessor = 2
    Renege = 3
    Arrival = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        def __lt__(self, other):
            if self.__class__ is other.__class__:
                return self.value > other.value
            return NotImplemented


def calculate_cdf(dist_parameter, x):
    return 1 - exp(- dist_parameter * x)


def gen_exp_value(dist_parameter):
    random_value = random()
    x = 0
    cdf = calculate_cdf(dist_parameter, x)
    while cdf < random_value:
        x += 1
        cdf = calculate_cdf(dist_parameter, x)
    return x


def simulate(total_number_of_processes, total_number_of_processors,
             inter_arrival_time_parameter, alpha, mu):
    inter_arrival_times = [gen_exp_value(inter_arrival_time_parameter) for _ in range(total_number_of_processes)]
    arrival_times = []
    sum_flag = 0
    for inter_arrival_time in inter_arrival_times:
        sum_flag += inter_arrival_time
        arrival_times.append(sum_flag)
    processes = [Process(arrival_time) for arrival_time in arrival_times]
    service_times_parameters = []
    for i in range(total_number_of_processors):
        service_times_parameters.append(list(map(float, input().split())))
    all_events = [Event(EventType.Arrival, process.arrival_time, process) for process in processes]
    events = [all_events[0]]
    heapq.heapify(events)
    processors = [Processor(i) for i in service_times_parameters]
    scheduler = Scheduler(mu)
    random_list = [i for i in range(Processor.core_numbers)]
    pointer = 1
    add_new_arrival_event = False

    while len(events) != 0 or pointer < 1_000_000:
        if pointer < 1_000_000 and add_new_arrival_event:
            heapq.heappush(events, all_events[pointer])
            pointer += 1
            add_new_arrival_event = False

        event = heapq.heappop(events)
        current_time = event.time
        process = event.process
        if event.type == EventType.Arrival:
            add_new_arrival_event = True
            new_event = Event(EventType.Renege,
                              current_time + gen_exp_value(1 / alpha),
                              process)
            heapq.heappush(events, new_event)
            if scheduler.is_busy:
                scheduler.queue_length_sum += (current_time - scheduler.previous_time) * (len(
                    scheduler.queue[0]) + len(scheduler.queue[1]))
                scheduler.previous_time = current_time
                scheduler.queue[process.priority].append(process)
            else:
                scheduler.is_busy = True
                new_event = Event(EventType.FindProcessor,
                                  current_time + gen_exp_value(scheduler.mu),
                                  process)
                heapq.heappush(events, new_event)
        elif event.type == EventType.FindProcessor:
            if event.valid:
                minimum = min(processors, key=lambda x: len(x.queue[0]) + len(x.queue[1]))
                minimum_processors = []
                for i in processors:
                    if len(i.queue[0]) + len(i.queue[1]) == len(minimum.queue[0]) + len(minimum.queue[1]):
                        minimum_processors.append(i)
                selected_processor = choice(minimum_processors)
                if len(selected_processor.queue[0]) + len(selected_processor.queue[1]) == 0:
                    all_busy = True
                    shuffle(random_list)
                    for i in random_list:
                        core = selected_processor.cores[i]
                        if not core.is_busy:
                            all_busy = False
                            core.is_busy = True
                            process.core = core
                            process.start_process_time = current_time
                            new_event = Event(EventType.Departure,
                                              current_time + gen_exp_value(core.service_time_parameter),
                                              process)
                            heapq.heappush(events, new_event)
                            break
                    if all_busy:
                        selected_processor.queue[process.priority].append(process)
                    else:
                        for i in range(len(events)):
                            e = events[i]
                            if e.process.id == process.id and e.type == EventType.Renege:
                                e.valid = False
                                break
                else:
                    selected_processor.queue_length_sum += (current_time - selected_processor.previous_time) * (len(
                        selected_processor.queue[0]) + len(selected_processor.queue[1]))
                    selected_processor.previous_time = current_time
                    selected_processor.queue[process.priority].append(process)
                if len(scheduler.queue[0]) + len(scheduler.queue[1]) == 0:
                    scheduler.is_busy = False
                else:
                    scheduler.queue_length_sum += (current_time - scheduler.previous_time) * (len(
                        scheduler.queue[0]) + len(scheduler.queue[1]))
                    scheduler.previous_time = current_time
                    if len(scheduler.queue[0]) != 0:
                        new_process = scheduler.queue[0][0]
                        del scheduler.queue[0][0]
                    else:
                        new_process = scheduler.queue[1][0]
                        del scheduler.queue[1][0]
                    new_event = Event(EventType.FindProcessor,
                                      current_time + gen_exp_value(scheduler.mu),
                                      new_process)
                    heapq.heappush(events, new_event)
        elif event.type == EventType.Renege:
            if event.valid:
                event.process.reneged = True
                event.process.process_time = -1
                found = False
                for i in scheduler.queue:
                    if event.process in i:
                        scheduler.queue_length_sum += (current_time - scheduler.previous_time) * (len(
                            scheduler.queue[0]) + len(scheduler.queue[1]))
                        scheduler.previous_time = current_time
                        i.remove(event.process)
                        found = True
                        break
                if not found:
                    for i in range(len(events)):
                        e = events[i]
                        if e.process.id == process.id and e.type == EventType.FindProcessor:
                            e.valid = False
                            found = True
                            break
                    if found:
                        if len(scheduler.queue[0]) + len(scheduler.queue[1]) == 0:
                            scheduler.is_busy = False
                        else:
                            scheduler.queue_length_sum += (current_time - scheduler.previous_time) * (len(
                                scheduler.queue[0]) + len(scheduler.queue[1]))
                            scheduler.previous_time = current_time
                            if len(scheduler.queue[0]) != 0:
                                new_process = scheduler.queue[0][0]
                                del scheduler.queue[0][0]
                            else:
                                new_process = scheduler.queue[1][0]
                                del scheduler.queue[1][0]
                            new_event = Event(EventType.FindProcessor,
                                              current_time + gen_exp_value(scheduler.mu),
                                              new_process)
                            heapq.heappush(events, new_event)
                    else:
                        for i in processors:
                            for q in i.queue:
                                if event.process in q:
                                    q.remove(event.process)
        elif event.type == EventType.Departure:
            process.finish_process_time = current_time
            process.process_time = process.finish_process_time - process.start_process_time
            process.core.total_busy_time += process.process_time
            empty_queue = True
            for q in process.core.processor.queue:
                if q:
                    empty_queue = False
                    process.core.processor.queue_length_sum += (
                                                                       current_time - process.core.processor.previous_time) * (
                                                                       len(
                                                                           process.core.processor.queue[0]) + len(
                                                                   process.core.processor.queue[1]))
                    process.core.processor.previous_time = current_time
                    process = q[0]
                    del q[0]
                    break
            if not empty_queue:
                process.start_process_time = current_time
                process.core = event.process.core
                new_event = Event(EventType.Departure,
                                  current_time + gen_exp_value(process.core.service_time_parameter),
                                  process)
                heapq.heappush(events, new_event)
                for i in range(len(events)):
                    e = events[i]
                    if e.process.id == process.id and e.type == EventType.Renege:
                        e.valid = False
                        break
            else:
                process.core.is_busy = False

    scheduler.queue_length_sum += (current_time - scheduler.previous_time) * (len(
        scheduler.queue[0]) + len(scheduler.queue[1]))
    for i in processors:
        i.queue_length_sum += (current_time - i.previous_time) * (len(i.queue[0]) + len(i.queue[1]))

    print('1:')
    value = sum([process.finish_process_time - process.arrival_time if process.process_time != -1 else 0 for process in
                 processes]) / sum([1 if process.process_time != -1 else 0 for process in processes])
    print(f'total mean: {value}')
    value = sum([
        process.finish_process_time - process.arrival_time if process.priority == 0 and process.process_time != -1 else 0
        for process in
        processes]) / sum(
        [1 if process.priority == 0 and process.process_time != -1 else 0 for process in processes])
    print(f'process type 1 mean: {value}')
    value = sum([
        process.finish_process_time - process.arrival_time if process.priority == 1 and process.process_time != -1 else 0
        for process in
        processes]) / sum(
        [1 if process.priority == 1 and process.process_time != -1 else 0 for process in processes])
    print(f'process type 2 mean: {value}')
    print('#################')
    print()

    print('2:')
    value = sum(
        [process.start_process_time - process.arrival_time if hasattr(process, 'start_process_time') else 0 for process in
         processes]) / sum([1 if hasattr(process, 'start_process_time') else 0 for process in processes])
    print(f'total waiting time mean: {value}')
    value = sum([process.start_process_time - process.arrival_time if process.priority == 0 and hasattr(process, 'start_process_time') else 0 for process in
                 processes]) / sum(
        [1 if process.priority == 0 and hasattr(process, 'start_process_time') else 0 for process in processes])
    print(f'process type 1 waiting time mean: {value}')
    value = sum([process.start_process_time - process.arrival_time if process.priority == 1 and hasattr(process, 'start_process_time') else 0 for process in
                 processes]) / sum(
        [1 if process.priority == 1 and hasattr(process, 'start_process_time') else 0 for process in processes])
    print(f'process type 2 waiting time mean: {value}')
    print('#################')
    print()

    print('3:')
    value = sum([1 if process.reneged else 0 for process in processes]) / len(processes) * 100
    print(f'total expired processes: {value}%')
    value = sum([1 if process.reneged and process.priority == 0 else 0 for process in processes]) / sum(
        [1 if process.priority == 0 else 0 for process in processes]) * 100
    print(f'process type 1 expired: {value}%')
    value = sum([1 if process.reneged and process.priority == 1 else 0 for process in processes]) / sum(
        [1 if process.priority == 1 else 0 for process in processes]) * 100
    print(f'process type 2 expired: {value}%')
    print('#################')
    print()

    print('4:')
    value = scheduler.queue_length_sum / current_time
    print(f'scheduler mean queue length: {value}')
    for i in range(len(processors)):
        processor = processors[i]
        value = processor.queue_length_sum / current_time
        print(f'processor {i + 1} mean queue length: {value}')


def main():
    lamb, alpha, mu = map(float, input().split())
    total_number_of_processes = 1_000_000
    total_number_of_processors = 5
    inter_arrival_time_parameter = lamb

    # FIFO
    simulate(total_number_of_processes, total_number_of_processors,
             inter_arrival_time_parameter, alpha, mu)


if __name__ == '__main__':
    main()
