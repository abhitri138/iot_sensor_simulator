import random
from collections import deque
from math import log
from statistics import mean, stdev
from math import ceil, pow


class Event:
    def __init__(self, st, at):
        self.st = st
        self.at = at


class Simulator:
    def __init__(self, mean_inter_arrival_time_RT, mean_inter_arrival_time_NRT
                 , mean_service_time_RT, mean_service_time_NRT
                 , RTCL, NRTCL, s, SCL, b, m):
        self.time_dict = {}
        seed = 10
        self.inter_arrival_time_RT_gen = random.Random(seed)
        self.inter_arrival_time_NRT_gen = random.Random(seed)
        self.service_time_RT_gen = random.Random(seed)
        self.service_time_NRT_gen = random.Random(seed)

        self.mean_inter_arrival_time_RT = mean_inter_arrival_time_RT
        self.mean_inter_arrival_time_NRT = mean_inter_arrival_time_NRT
        self.mean_service_time_RT = mean_service_time_RT
        self.mean_service_time_NRT = mean_service_time_NRT

        self.MC = 0

        self.time_dict["RTCL"] = RTCL
        self.time_dict["NRTCL"] = NRTCL
        self.time_dict["SCL"] = SCL
        # self.nRT = nRT
        self.nRT = deque([])
        # self.nNRT = nNRT
        self.nNRT = deque([Event(self.get_service_time_NRT(), 0)])
        self.s = s
        self.rt_response_times = []
        self.nrt_response_times = []
        self.current_event = Event(self.get_service_time_NRT(), 0)
        self.m = m
        self.b = b
        self.nonRT_remaining = 0
        self.rt_mean_list = []
        self.nrt_mean_list = []
        self.rt_percent_list = []
        self.nrt_percent_list = []
        self.percent_idx = ceil(0.95 * b)
        self.t_val = 2.009  # 1.677

    def get_inter_arrival_time_RT(self):
        return -1 * self.mean_inter_arrival_time_RT * log(self.inter_arrival_time_RT_gen.random())

    def get_inter_arrival_time_NRT(self):
        return -1 * self.mean_inter_arrival_time_NRT * log(self.inter_arrival_time_NRT_gen.random())

    def get_service_time_RT(self):
        return -1 * self.mean_service_time_RT * log(self.service_time_RT_gen.random())

    def get_service_time_NRT(self):
        return -1 * self.mean_service_time_NRT * log(self.service_time_NRT_gen.random())

    def update_response_list_on_exit(self):
        if self.s == 1:
            self.rt_response_times.append(self.MC - self.current_event.at)
        elif self.s == 2:
            self.nrt_response_times.append(self.MC - self.current_event.at)

    def rt_event_arrival(self):
        add_time = self.get_inter_arrival_time_RT()
        # self.nRT += 1
        self.nRT.append(Event(self.get_service_time_RT(), self.MC))
        if self.s == 2:
            self.nonRT_remaining = (self.time_dict["SCL"] - self.MC)
            if self.nonRT_remaining > 0:
                # self.nNRT += 1
                self.nNRT.insert(0, Event(self.nonRT_remaining, self.current_event.at))
        if self.s != 1:
            # self.nRT -= 1
            self.current_event = self.nRT.popleft()
            self.s = 1
            self.time_dict["SCL"] = self.MC + self.current_event.st
        self.time_dict['RTCL'] += add_time

    def nrt_event_arrival(self):
        add_time = self.get_inter_arrival_time_NRT()
        # self.nNRT += 1
        self.nNRT.append(Event(self.get_service_time_NRT(), self.MC))
        if self.s == 0:
            # self.nNRT -= 1
            self.current_event = self.nNRT.popleft()
            self.s = 2
            self.time_dict["SCL"] = self.MC + self.current_event.st
        self.time_dict['NRTCL'] += add_time

    def service_completion(self):
        self.update_response_list_on_exit()
        if len(self.nRT) > 0:
            # self.nRT -= 1
            self.current_event = self.nRT.popleft()
            self.s = 1
            self.time_dict["SCL"] = self.MC + self.current_event.st
        elif len(self.nNRT) > 0:
            self.current_event = self.nNRT.popleft()
            self.s = 2
            if self.nonRT_remaining > 0:
                self.time_dict["SCL"] = self.MC + self.nonRT_remaining
                self.nonRT_remaining = 0
            else:
                self.time_dict["SCL"] = self.MC + self.current_event.st
        else:
            self.s = 0

    def process_batch(self):
        rt = self.rt_response_times[:self.b]
        nrt = self.nrt_response_times[:self.b]
        self.rt_mean_list.append(mean(rt))
        self.nrt_mean_list.append(mean(nrt))
        self.rt_percent_list.append(sorted(rt)[self.percent_idx])  # check once
        self.nrt_percent_list.append(sorted(nrt)[self.percent_idx])
        self.rt_response_times = self.rt_response_times[self.b - 1:-1]
        self.nrt_response_times = self.nrt_response_times[self.b - 1:-1]

    def get_rt_confidence_interval(self, mean):
        rt_sd = stdev(self.rt_mean_list)
        return mean - self.t_val * rt_sd / pow(len(self.rt_mean_list), 0.5), mean + self.t_val * rt_sd / pow(
            len(self.rt_mean_list), 0.5)

    def get_nrt_confidence_interval(self, mean):
        nrt_sd = stdev(self.nrt_mean_list)
        return mean - self.t_val * nrt_sd / pow(len(self.nrt_mean_list), 0.5), \
               mean + self.t_val * nrt_sd / pow(len(self.nrt_mean_list), 0.5)

    def run_batch(self):
        row_format = "{:>22}" * 8

        # print(row_format.format("MC",
        #                         "RTCL",
        #                         "nonRTCL",
        #                         "nRT",
        #                         "nNonRT",
        #                         "SCL",
        #                         "Server status",
        #                         "    pre-empted service time"))
        #
        # print(row_format.format(self.MC,
        #                         self.time_dict["RTCL"],
        #                         self.time_dict["NRTCL"],
        #                         len(self.nRT),
        #                         len(self.nNRT),
        #                         self.time_dict["SCL"],
        #                         self.s,
        #                         ("s=" + str(self.nonRT_remaining) if self.nonRT_remaining > 0 else "")))
        while len(self.rt_response_times) < self.b or len(self.nrt_response_times) < self.b:
            min_clk = min(self.time_dict, key=self.time_dict.get)
            if self.s == 0:
                min_clk = 'RTCL' if self.time_dict['RTCL'] <= self.time_dict['NRTCL'] else \
                    'NRTCL'
            self.MC = self.time_dict[min_clk]

            if min_clk.__eq__("RTCL"):
                self.rt_event_arrival()
            if min_clk.__eq__("NRTCL"):
                self.nrt_event_arrival()
            if min_clk.__eq__("SCL"):
                self.service_completion()
            # print(row_format.format(self.MC,
            #                         self.time_dict["RTCL"],
            #                         self.time_dict["NRTCL"],
            #                         len(self.nRT),
            #                         len(self.nNRT),
            #                         self.time_dict["SCL"],
            #                         self.s,
            #                         self.nonRT_remaining))

    def run(self):
        self.run_batch()
        for number in range(1, self.m):
            self.run_batch()
            self.process_batch()
        return mean(self.rt_mean_list), mean(self.nrt_mean_list)

        # print("R(RT) mean: {a}, 95th percentile:{b}, Confidence Interval:{c}".format(a=mean(self.rt_mean_list),
        #                                                                              b=mean(self.rt_percent_list),
        #                                                                              c=self.get_rt_confidence_interval(
        #                                                                                  mean(self.rt_mean_list))))
        # print("R(NonRT) mean: {a}, 95th percentile:{b}, Confidence Interval:{c}".format(a=mean(self.nrt_mean_list),
        #                                                                                 b=mean(self.nrt_percent_list),
        #                                                                                 c=self.get_nrt_confidence_interval(
        #                                                                                     mean(self.nrt_mean_list))))


if __name__ == "__main__":
    # inter_arrival_time_RT = int(input("Enter Mean Inter Arrival Time RT:"))
    # inter_arrival_time_NRT = int(input("Enter Mean Inter Arrival Time nonRT:"))
    # service_time_RT = int(input("Enter Mean Service Time RT:"))
    # service_time_NRT = int(input("Enter Mean Service Time nonRT:"))
    # m = int(input("Enter number of batches(m):"))
    # b = int(input("Enter batch size:"))
    mrt = []
    mnrt = []
    lnrt = []
    inter_arrival_time_RT = 7
    inter_arrival_time_NRT = []
    service_time_RT = 2
    service_time_NRT = 4
    m = 51
    b = 1000

    simulator = Simulator(inter_arrival_time_RT,
                          inter_arrival_time_NRT,
                          service_time_RT,
                          service_time_NRT,
                          RTCL=3,
                          NRTCL=5,
                          s=2,
                          SCL=4,
                          b=b,
                          m=m)
    for i in range(10, 45, 5):
        simulator.mean_inter_arrival_time_NRT = i
        m1, m2 = simulator.run()
        mrt.append(m1)
        mnrt.append(m2)
        lnrt.append(1/i)

    print(mrt)
    print(mnrt)
    print(lnrt)

