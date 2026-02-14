import time

class TrafficSignalSystem:
    def __init__(self):
        self.lanes = ["Lane A", "Lane B", "Lane C", "Lane D"]
        self.vehicle_counts = {lane: 0 for lane in self.lanes}

        self.signal_state = {lane: "RED" for lane in self.lanes}
        self.current_lane = self.lanes[0]
        self.signal_state[self.current_lane] = "GREEN"

        self.green_time = 15
        self.last_switch_time = time.time()

        self.ambulance_mode = False
        self.ambulance_lane = None

    def update_vehicle_counts(self, counts):
        self.vehicle_counts.update(counts)

    def calculate_green_time(self, lane):
        vehicles = self.vehicle_counts[lane]

        if vehicles <= 5:
            return 10
        elif vehicles <= 15:
            return 20
        elif vehicles <= 30:
            return 35
        else:
            return 50

    def switch_lane(self):
        idx = self.lanes.index(self.current_lane)
        next_idx = (idx + 1) % len(self.lanes)

        self.signal_state[self.current_lane] = "RED"
        self.current_lane = self.lanes[next_idx]
        self.signal_state[self.current_lane] = "GREEN"

        self.green_time = self.calculate_green_time(self.current_lane)
        self.last_switch_time = time.time()

    def update(self):
        if self.ambulance_mode:
            return

        elapsed = time.time() - self.last_switch_time
        if elapsed >= self.green_time:
            self.switch_lane()

    def set_ambulance_priority(self, lane):
        self.ambulance_mode = True
        self.ambulance_lane = lane

        for l in self.lanes:
            self.signal_state[l] = "RED"

        self.signal_state[lane] = "GREEN"

    def clear_ambulance_priority(self):
        self.ambulance_mode = False
        self.ambulance_lane = None

        for l in self.lanes:
            self.signal_state[l] = "RED"

        self.current_lane = self.lanes[0]
        self.signal_state[self.current_lane] = "GREEN"
        self.green_time = self.calculate_green_time(self.current_lane)
        self.last_switch_time = time.time()

    def get_status(self):
        return {
            "vehicle_counts": self.vehicle_counts,
            "signal_state": self.signal_state,
            "current_lane": self.current_lane,
            "green_time": self.green_time,
            "ambulance_mode": self.ambulance_mode,
            "ambulance_lane": self.ambulance_lane
        }
