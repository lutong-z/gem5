from argparse import ArgumentParser


def addSECommonOption(parser : ArgumentParser) :
    parser.add_argument(
        "-c",
        "--cmd",
        default="",
        help="The binary to run in syscall emulation mode.",
        required=True
    )
    parser.add_argument(
        "-o",
        "--options",
        default="",
        help="""The options to pass to the binary, use " "
                              around the entire string""",
    )
    parser.add_argument(
        "-I",
        "--maxinsts",
        action="store",
        type=int,
        default=None,
        help="""Total number of instructions to
                                            simulate (default: run forever)""",
    )

def addSimpointOption(parser : ArgumentParser) :
    # Simpoint options
    parser.add_argument(
        "--simpoint-profile",
        action="store_true",
        help="Enable basic block profiling for SimPoints",
    )
    parser.add_argument(
        "--simpoint-interval",
        type=int,
        default=10000000,
        help="SimPoint interval in num of instructions, default 10000000",
    )
    parser.add_argument(
        "--warmup-interval",
        type=int,
        default=1000000,
        help="Warmup interval in num of instructions, default 1000000",
    )
    parser.add_argument(
        "--take-simpoint-checkpoints",
        action="store",
        type=str,
        help="<simpoint file,weight file>",
    )
    parser.add_argument(
        "--restore-simpoint-checkpoint",
        action="store_true",
        help="restore from a checkpoint taken with "
    )
    parser.add_argument(
        "--checkpoint-dir",
        action="store",
        type=str,
        help="Restorce checkpoint in this absolute directory",
    )