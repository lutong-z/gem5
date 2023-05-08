from ResearchPlatform.platforms.RiosSEPlatform import RiosSEPlatform
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.memory import SingleChannelDDR4_2400


cache = PrivateL1PrivateL2CacheHierarchy(
    l1i_size  = "32kB",
    l1d_size  = "32kB",
    l2_size   = "256kB",
)

# We use a single channel DDR3_1600 memory system
memory = SingleChannelDDR4_2400(size="3GB")

# We use a simple Timing processor with one core.
core = SimpleProcessor(
    cpu_type=CPUTypes.O3, isa=ISA.RISCV, num_cores=1
)

platform = RiosSEPlatform(clk_freq="1GHz", core=core, memory=memory, cache_hierarchy=cache)

args = platform.parse_arguments()

platform.simulate(args)