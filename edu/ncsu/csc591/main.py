from edu.ncsu.csc591.simulator import Simulator


def task1_1(inter_arrival_time_RT,
            inter_arrival_time_NRT,
            service_time_RT,
            service_time_NRT):
    simulator = Simulator(inter_arrival_time_RT,
                          inter_arrival_time_NRT,
                          service_time_RT,
                          service_time_NRT,
                          RTCL=3,
                          NRTCL=5,
                          nRT=0,
                          nNRT=0,
                          s=2,
                          SCL=4)
    simulator.run(50)


def task1_2(inter_arrival_time_RT,
            inter_arrival_time_NRT,
            service_time_RT,
            service_time_NRT):
    simulator = Simulator(inter_arrival_time_RT=5,
                          inter_arrival_time_NRT=10,
                          service_time_RT=4,
                          service_time_NRT=2,
                          RTCL=3,
                          NRTCL=5,
                          nRT=0,
                          nNRT=0,
                          s=2,
                          SCL=4)
    simulator.run(20)


if __name__ == "__main__":
    # inter_arrival_time_RT = input()
    # inter_arrival_time_NRT = input()
    # service_time_RT = input()
    # service_time_NRT = input()
    inter_arrival_time_RT = 10
    inter_arrival_time_NRT = 5
    service_time_RT = 2
    service_time_NRT = 4
    print("************************************Task 1.1*************************************")
    task1_1(inter_arrival_time_RT, inter_arrival_time_NRT, service_time_RT, service_time_NRT)
    print("************************************Task 1.2*************************************")
    task1_2(inter_arrival_time_RT, inter_arrival_time_NRT, service_time_RT, service_time_NRT)
