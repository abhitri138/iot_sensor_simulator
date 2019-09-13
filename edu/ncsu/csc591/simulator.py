class Simulator:
    def __init__(self, inter_arrival_time_RT, inter_arrival_time_NRT
                 ,service_time_RT, service_time_NRT
                 ,RTCL, NRTCL, nRT, nNRT, s, SCL):
        self.time_dict = {}
        self.inter_arrival_time_RT = inter_arrival_time_RT
        self.inter_arrival_time_NRT = inter_arrival_time_NRT
        self.service_time_RT = service_time_RT
        self.service_time_NRT = service_time_NRT
        self.MC = 0

        self.time_dict["RTCL"] = RTCL
        self.time_dict["NRTCL"] = NRTCL
        self.time_dict["SCL"] = SCL
        self.nRT = nRT
        self.nNRT = nNRT
        self.s = s


    def run(self, mc_limit):
        nonRT_remaining = 0
        row_format = "{:>22}" * 8
        print(row_format.format("MC",
                                "RTCL",
                                "nonRTCL",
                                "nRT",
                                "nNonRT",
                                "SCL",
                                "Server status",
                                "    pre-empted service time"))

        print(row_format.format(self.MC,
                                self.time_dict["RTCL"],
                                self.time_dict["NRTCL"],
                                self.nRT,
                                self.nNRT,
                                self.time_dict["SCL"],
                                self.s,
                                ("s=" + str(nonRT_remaining) if nonRT_remaining > 0 else "")))

        while self.MC <= mc_limit:
            min_clk = min(self.time_dict, key=self.time_dict.get)
            self.MC = self.time_dict[min_clk]
            add_time = 0
            if min_clk.__eq__("RTCL"):
                add_time = self.inter_arrival_time_RT
                self.nRT += 1
                if self.s == 2:
                    nonRT_remaining = (self.time_dict["SCL"] - self.MC)
                    if nonRT_remaining > 0:
                        self.nNRT += 1
                if self.s != 1:
                    self.nRT -= 1
                    self.s = 1
                    self.time_dict["SCL"] = self.MC + self.service_time_RT
            if min_clk.__eq__("NRTCL"):
                add_time = self.inter_arrival_time_NRT
                self.nNRT += 1
            if min_clk.__eq__("SCL"):
                if self.nRT > 0:
                    self.nRT -= 1
                    self.s = 1
                    add_time = self.service_time_RT
                elif self.nNRT > 0:
                    self.nNRT -= 1
                    self.s = 2
                    if(nonRT_remaining > 0):
                        self.time_dict["SCL"] = self.MC + nonRT_remaining
                        nonRT_remaining = 0
                    else:
                        self.time_dict["SCL"] = self.MC + self.service_time_NRT
                else:
                    self.s = 0
            if not min_clk.__eq__("SCL"):
                self.time_dict[min_clk] += add_time
            pre_service_time = ("s=" + str(nonRT_remaining) if nonRT_remaining > 0 else "")
            print(row_format.format(self.MC,
                                    self.time_dict["RTCL"],
                                    self.time_dict["NRTCL"],
                                    self.nRT,
                                    self.nNRT,
                                    self.time_dict["SCL"],
                                    self.s,
                                    nonRT_remaining))