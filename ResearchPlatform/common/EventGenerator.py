import m5
from os.path import join as joinpath
from gem5.simulate.simulator import Simulator
from gem5.utils.simpoint import SimPoint
from m5.stats import reset, dump

def take_simpoint_checkpoints(simulator : Simulator, simpoint : SimPoint, cptdir : str) : 
    # Get Simpoint Information
    sp_start_insts = simpoint.get_simpoint_start_insts()
    sp_weight = simpoint.get_weight_list()
    sp_interval_length = simpoint.get_simpoint_interval()
    sp_warmup_length = simpoint.get_warmup_list()
    
    # Start Checkpointing
    simpoint_number = len(sp_start_insts)
    for simpoint_index in range(simpoint_number) : 
        start_insts         = sp_start_insts[simpoint_index]
        weight              = sp_weight[simpoint_index]
        interval_length     = sp_interval_length
        warmup_length       = sp_warmup_length[simpoint_index]
        
        cpt_path = joinpath(
                cptdir,
                "cpt.simpoint_%02d_inst_%d_weight_%f_interval_%d_warmup_%d"
                % (
                    simpoint_index,
                    start_insts,
                    weight,
                    interval_length,
                    warmup_length,
                ),
        )
        
        print("**************** Start simpoint {} ****************\n".format(simpoint_index))
        print("Saving path          = {}\n".format(cpt_path))
        print("start_insts          = {}\n".format(start_insts))
        print("weight               = {}\n".format(weight))
        print("interval_length      = {}\n".format(interval_length))
        print("warmup_length        = {}\n".format(warmup_length))
        print("****************  End simpoint  {} ****************\n".format(simpoint_index))
        
        # Save checkpoint
        m5.checkpoint(cpt_path)
        yield False

def restore_simpoint_checkpoint(simulator : Simulator, simpoint_interval : int, warmup_interval : int) : 
    warmup_done = False
    while True : 
        if not warmup_done : 
            print("**************** End simpoint warmup ****************\n")
            print("**************** Start simpoint simulation ***************\n")
            warmup_done = True
            reset()
            simulator.schedule_max_insts(simpoint_interval-warmup_interval)
            yield False
        else : 
            print("**************** End simpoint simulation ****************\n")
            yield True