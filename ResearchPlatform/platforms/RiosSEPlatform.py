import argparse
import m5
from m5.util import addToPath, fatal, warn
from pathlib import Path
from gem5.components.cachehierarchies.abstract_cache_hierarchy import AbstractCacheHierarchy
from gem5.components.memory.abstract_memory_system import AbstractMemorySystem
from gem5.components.processors.abstract_processor import AbstractProcessor
from gem5.simulate.exit_event import ExitEvent
from gem5.resources.resource import CustomResource
from gem5.utils.simpoint import SimPoint
from gem5.components.boards.simple_board import SimpleBoard
from gem5.simulate.simulator import Simulator
from gem5.components.processors.cpu_types import CPUTypes
from ResearchPlatform.common.RiosPlatformOptions import addSECommonOption,addSimpointOption
from ResearchPlatform.common.EventGenerator import take_simpoint_checkpoints,restore_simpoint_checkpoint
from argparse import ArgumentParser

class RiosSEPlatform(SimpleBoard) : 
    def __init__(self, clk_freq: str, core: AbstractProcessor, 
                 memory: AbstractMemorySystem, cache_hierarchy: AbstractCacheHierarchy) -> None:
        super().__init__(clk_freq, core, memory, cache_hierarchy)
    
    def parse_arguments(self, additionalOption = None) : 

        parser = argparse.ArgumentParser(
            description= "Gem5-SE processor simulation platform of RIOSLab"
        )

        addSECommonOption(parser)       
        addSimpointOption(parser)

        if additionalOption is not None : 
            additionalOption(parser)
        
        return parser.parse_args()
    
    def simulate(self,args) :
        
        simulator = Simulator(board=self,full_system=False)
        
        # Three working mode : Normal, Take SimPoint, Restore SimPoint
        workload = CustomResource(args.cmd)
        runtime_options = args.options.split()
        if args.restore_simpoint_checkpoint: 
            if not args.checkpoint_dir :
                fatal("Checkpoint dir path should be set")
                
            checkpoint = Path(args.checkpoint_dir)
            simpoint_interval = args.simpoint_interval
            warmup_interval = args.warmup_interval
            self.set_se_binary_workload(
                binary=workload,
                arguments=runtime_options,
                checkpoint=checkpoint
            )
            if warmup_interval > 0 :
                simulator._on_exit_event[ExitEvent.MAX_INSTS] = restore_simpoint_checkpoint(simulator,simpoint_interval,warmup_interval)
                simulator.schedule_max_insts(warmup_interval)
                print("**************** Start simpoint warmup ****************\n")
            else : 
                simulator.schedule_max_insts(simpoint_interval)
                
        elif args.take_simpoint_checkpoints is not None:
            if args.checkpoint_dir:
                cptdir = args.checkpoint_dir
            else :
                cptdir = m5.options.outdir
            (
            simpoint_filename, 
            weight_filename
            ) = args.take_simpoint_checkpoints.split(",", 3)
            simpoint_interval = args.simpoint_interval
            warmup_interval = args.warmup_interval
            print("simpoint analysis file:", simpoint_filename)
            print("simpoint weight file:", weight_filename)
            print("interval length:", simpoint_interval)
            print("warmup length:", warmup_interval)
            simpoint = SimPoint(
                simpoint_file_path= simpoint_filename,
                weight_file_path=weight_filename,
                simpoint_interval=int(simpoint_interval),
                warmup_interval=int(warmup_interval)
            )
            self.set_se_simpoint_workload(
                binary=workload,
                arguments=runtime_options,
                simpoint=simpoint
            )
            simulator._on_exit_event[ExitEvent.SIMPOINT_BEGIN] = take_simpoint_checkpoints(simulator,simpoint,cptdir)
        else:
            self.set_se_binary_workload(
                binary=workload,
                arguments=runtime_options
            )
            
        # SimPoint Profiling
        if args.simpoint_profile : 
            simpoint_interval = args.simpoint_interval
            cores = self.get_processor().cores
            if cores[0].get_type() != CPUTypes.ATOMIC : 
                fatal("SimPoint/BPProbe should be done with an atomic cpu")
            if len(cores) > 1:
                fatal("SimPoint generation not supported with more than one CPUs")
            for cpu in self.get_processor().cores : 
                cpu.core.addSimPointProbe(simpoint_interval)
                
        # MaxInsns
        if args.maxinsts is not None: 
            simulator.schedule_max_insts(args.maxinsts)
     
        simulator.run()

        print(
            "Exiting @ tick {} because {}.".format(
                simulator.get_current_tick(), simulator.get_last_exit_event_cause()
            )
        )