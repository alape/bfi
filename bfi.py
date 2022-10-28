from argparse import ArgumentParser

from machine import BFMachine


def interactive_mode(vm: BFMachine):
    print("Running BFI in interactive mode. Enter \"q\" or Ctrl-C to exit, \"s\" for status information.")
    try:
        while True:
            cmd = input("§ ")
            if cmd in ("q", "Q"):
                raise KeyboardInterrupt
            elif cmd in ("s", "S"):
                print(f"Stack: {vm.stack}, memory position: {vm.memory.mc}, memory value: {vm.memory.get()}")
            else:
                vm.eval(cmd)
    except KeyboardInterrupt:
        print("\nKTHXBYE")


if __name__ == "__main__":
    parser = ArgumentParser(description='bfi: Brainfuck interpreter')
    parser.add_argument("--trace", action="store_true", help="Enable tracing")
    parser.add_argument("--debug", action="store_true", help="Enable step-by-step debug")
    parser.add_argument("--mem", type=int, default=30000, help="VM memory size in bytes (30000 by default)")
    parser.add_argument("-c", "--c_code", metavar="OUTPUT_FILE", type=str, default=None, help="Compile to C code")
    parser.add_argument("filename", metavar="FILE", type=str, nargs="?", default=None,
                        help="Source file path")

    args = parser.parse_args()

    vm = BFMachine(args.mem)
    vm.debug = args.debug
    vm.trace = args.trace

    if args.c_code:
        vm.c_compile_file(args.filename, args.c_code)
    else:
        if vm.debug or vm.trace:
            print(f"{'Debugging' if vm.debug else 'Tracing'} enabled.")
            if vm.debug:
                print("Debug: <> or Return to advance.")

        if args.filename:
            vm.process_file(args.filename)
        else:
            interactive_mode(vm)
