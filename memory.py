from common import BFRuntimeError


class BFVMemory:
    def __init__(self, length: int = 30000) -> None:
        self._contents = [0] * length
        self._len = length
        self.mc = 0

    def __len__(self) -> int:
        return self._len

    def set_address_delta(self, delta: int) -> None:
        self.mc += delta
        if not 0 <= self.mc <= self._len -1:
            self.mc -= delta
            raise BFRuntimeError(f"out of memory: {self.mc + delta}")

    def set_value_delta(self, delta: int) -> None:
        self._contents[self.mc] += delta
        if self._contents[self.mc] < 0:
            self._contents[self.mc] = 0

    def incr_address(self) -> None:
        self.set_address_delta(1)

    def decr_address(self) -> None:
        self.set_address_delta(-1)

    def incr_value(self) -> None:
        self.set_value_delta(1)

    def decr_value(self) -> None:
        self.set_value_delta(-1)

    def get(self) -> int:
        return self._contents[self.mc]

    def set(self, value: int) -> None:
        self._contents[self.mc] = value
