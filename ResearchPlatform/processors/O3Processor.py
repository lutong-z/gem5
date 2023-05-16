from ResearchPlatform.platforms.RiosSEPlatform import RiosSEPlatform
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.memory import SingleChannelDDR4_2400
from m5.objects.BranchPredictor import *
from m5.params import Param
from m5.stats import reset, dump
import argparse

cache = PrivateL1PrivateL2CacheHierarchy(
    l1i_size  = "32kB",
    l1d_size  = "32kB",
    l2_size   = "256kB",
)

# We use a single channel DDR4_2400 memory system
memory = SingleChannelDDR4_2400(size="3GB")

# We use a simple Timing processor with one core.
core = SimpleProcessor(
    cpu_type=CPUTypes.O3, isa=ISA.RISCV, num_cores=1
)

platform = RiosSEPlatform(clk_freq="1GHz", core=core, memory=memory, cache_hierarchy=cache)


def add_option(parser : argparse.ArgumentParser) : 
    parser.add_argument(
        "--rob_size",
        type=int,
        help="reorder buffer size of processor",
        default=128
    )

    parser.add_argument(
        "--lq_size",
        type=int,
        help="load queue size of processor",
    )

    parser.add_argument(
        "--sq_size",
        type=int,
        help="store queue size of processor",
    )

    parser.add_argument(
        "--iq_size",
        type=int,
        help="issue queue size of processor",
    )

    parser.add_argument(
        "--gpr_size",
        type=int,
        help="general propose register size of processor",
    )

args = platform.parse_arguments(add_option)

rob_size = args.rob_size
lq_size  = args.lq_size
sq_size  = args.sq_size
iq_size  = args.iq_size
gpr_size = args.gpr_size

for cpu in core.get_cores() : 
    
    cpu.core.numROBEntries = rob_size
    cpu.core.LQEntries = lq_size if lq_size else rob_size * 0.3
    cpu.core.SQEntries = sq_size if sq_size else rob_size * 0.3
    cpu.core.numIQEntries = iq_size if iq_size else rob_size * 0.5
    cpu.core.numPhysIntRegs = gpr_size if gpr_size else rob_size

platform.simulate(args)
