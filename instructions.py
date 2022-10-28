from typing import Callable

from common import BFRuntimeError


class BFInstruction:
    arguments: dict
    _fn: Callable

    def __str__(self) -> str:
        return f"{self.__class__.__name__.removeprefix('BF').removesuffix('Instruction')}" \
               f"{str(list(self.arguments.values()))}"

    def apply(self, vm: "BFMachine") -> None:
        self._fn(self, vm)

    def to_c_code(self) -> str:
        return ";\n"

    @classmethod
    def make(cls, *args, **kwargs):
        i = cls()
        i.arguments = kwargs
        i._fn = i._generate_fn(i.arguments)
        return i

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            pass
        return fn


class BFMemoryShiftInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return f"i += {self.arguments['delta']};"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            vm.memory.set_address_delta(args["delta"])
        return fn


class BFMemorySetInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return f"mem[i] += {self.arguments['delta']};"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            vm.memory.set_value_delta(args["delta"])
        return fn


class BFMemoryZeroInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return "mem[i] = 0;"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            vm.memory.set(0)
        return fn


class BFInputInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return "mem[i] = getchar();"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            vm.memory.set(ord(input()))
        return fn


class BFOutputInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return "putchar(mem[i]);"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            print(chr(vm.memory.get()), end="")
        return fn


class BFEnterCycleInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return "while(mem[i]) {"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            if not vm.memory.get():
                refc = 1

                # skip to the correct closing parenthesis
                while refc:
                    vm.pc += 1
                    if type(vm.program[vm.pc]) is BFEnterCycleInstruction:
                        refc += 1
                    elif type(vm.program[vm.pc]) is BFEndCycleInstruction:
                        refc -= 1
            else:
                vm.stack.append(vm.pc)
        return fn


class BFEndCycleInstruction(BFInstruction):
    def to_c_code(self) -> str:
        return "}"

    @staticmethod
    def _generate_fn(args: dict) -> Callable:
        def fn(self, vm: "BFMachine") -> None:
            try:
                if vm.memory.get():
                    vm.pc = vm.stack.pop() - 1
                else:
                    vm.stack.pop()
            except IndexError:
                raise BFRuntimeError("unmatched parenthesis")
        return fn


if __name__=="__main__":
    from machine import BFMachine
    vm = BFMachine()
    i = BFMemorySetInstruction.make(delta=1)
    i.apply(vm)
    print(vm.memory.get())

