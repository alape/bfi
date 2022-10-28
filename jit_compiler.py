from instructions import *

from typing import List


class BFJITCompiler:
    def __init__(self):
        self._reset()
        self._instr_map = {
            ".": BFOutputInstruction,
            ",": BFInputInstruction,
            "[": BFEnterCycleInstruction,
            "]": BFEndCycleInstruction
        }

    def _reset(self) -> None:
        self.cntr = 0
        self.source = ""
        self.sequence_instr = ""
        self.sequence_length = 0

    def _finalize_sequence(self) -> List[BFInstruction]:
        if self.sequence_length:
            delta = self.sequence_length * (1 if self.sequence_instr in ("+", ">") else -1)
            cls = BFMemorySetInstruction if self.sequence_instr in ("+", "-") else \
                BFMemoryShiftInstruction
            self.sequence_instr = ""
            self.sequence_length = 0
            return [cls.make(delta=delta)]
        else:
            return []

    def parse(self, string: str) -> List[BFInstruction]:
        self._reset()
        self.source = string

        output = []

        while self.cntr < len(self.source):
            if self.source[self.cntr:self.cntr+3] == "[-]":
                output += self._finalize_sequence()
                output.append(BFMemoryZeroInstruction.make())
                self.cntr += 3
            else:
                char = self.source[self.cntr]
                if char in (".", ",", "[", "]"):
                    output += self._finalize_sequence()
                    output.append(self._instr_map[char].make())
                elif char in ("<", ">", "+", "-"):
                    if char == self.sequence_instr:
                        self.sequence_length += 1
                    else:
                        output += self._finalize_sequence()
                        self.sequence_instr = char
                        self.sequence_length = 1
                self.cntr += 1
        output += self._finalize_sequence()
        return output


if __name__ == "__main__":
    bytecode = BFJITCompiler().parse("++[>+++++++++++++++++++++++++++"
                                     "+++++++++++++++++++++++++[>++++[-]<-.]<-]")
    for i in bytecode:
        print(str(i))
