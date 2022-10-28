from typing import List, Union

from jit_compiler import BFJITCompiler
from memory import BFVMemory
from common import BFRuntimeError
from instructions import BFEnterCycleInstruction, BFEndCycleInstruction

class BFMachine:
    def __init__(self, mem_size: int = 30000) -> None:
        self.memory = BFVMemory(mem_size)
        self.pc = 0
        self.stack = []
        self.program = []
        self.skip = False
        self.trace = False
        self.debug = False

    def _print_status(self, terminate: bool = False):
        print(f"PC:{self.pc}; INSTR:\"{str(self.program[self.pc])}\"; MC:{self.memory.mc}; MV:{self.memory.get()};"
              f" STK:{str(self.stack)}", end="\n" if terminate else "")

    def _parse(self, statement: Union[List[str], str]):
        self.program = BFJITCompiler().parse(
            statement if type(statement) == str else "".join(statement))

        if self.trace or self.debug:
            print(f"Compiled input: {len(statement)} -> {len(self.program)} instructions")
            for addr, i in enumerate(self.program):
                print(f"{hex(addr)}:\t{str(i)}")

    def eval(self, statement: Union[List[str], str]) -> None:
        self._parse(statement)
        self.pc = 0

        while self.pc < len(self.program):
            try:
                if self.trace or self.debug:
                    self._print_status(self.trace)
                    if self.debug:
                        try:
                            cmd = input("?")
                        except KeyboardInterrupt:
                            print("\nClosing the debugger.")
                            return
                        if cmd:
                            if cmd == ">":
                                self.pc += 1
                                continue
                            elif cmd in "<":
                                self.pc -= 1 if self.pc > 0 else 0
                                continue
                            else:
                                print(f"Unknown debug statement: {cmd}")

                self.program[self.pc].apply(self)
                self.pc += 1

            except BFRuntimeError as e:
                print(f"\n=== Runtime error: {e} ===")
                self._print_status(True)
                return

    def process_file(self, filename: str) -> None:
        with open(filename) as f:
            self.eval(f.read())

    def c_compile_file(self, in_filename: str, output_filename: str) -> None:
        with open(in_filename) as f:
            code = self.to_c_code(f.read())

        with open(output_filename, "w") as f:
            f.write(code)

    def to_c_code(self, statement: Union[List[str], str]) -> str:
        self._parse(statement)

        indent_level = 1
        code = "#include <stdio.h>\n#include <string.h>\n\n"
        code += f"int i = 0;\nchar mem[{len(self.memory)}];\n\n"
        code += "int main(void) {\n  memset(mem, 0, sizeof(mem));\n"

        for i in self.program:
            if type(i) == BFEndCycleInstruction:
                indent_level -= 1
            code += f"{'  ' * indent_level}{i.to_c_code()}\n"
            if type(i) == BFEnterCycleInstruction:
                indent_level += 1

        code += "  return 0;\n}\n"
        return code

if __name__ == "__main__":
    m = BFMachine()
    m.trace = True
    m.process_file("samples/hello.b")
