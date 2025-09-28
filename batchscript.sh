#!/bin/bash -l
#SBATCH --time=13:30:00
#SBATCH --ntasks=4         # Increase number of tasks to match nproc_per_node
#SBATCH --cpus-per-task=4  # Allocate 4 CPUs per task for data loading workers
#SBATCH --mem=50g
#SBATCH --tmp=10g
#SBATCH --mail-type=ALL
#SBATCH --mail-user=radke149@umn.edu
#SBATCH -p a100-4       
#SBATCH --gres=gpu:a100:2  # Request 2 GPUs to match nproc_per_node


cd /scratch.global/radke149/KSRL_codebase

module load cuda/12.1.1


source /scratch.global/radke149/dicl-ksrl-py11


conda activate /scratch.global/radke149/dicl-ksrl-py11


echo "Job started at: $(date)"

dicl-sac --seed $RANDOM --env-id HalfCheetah-v4 --total-timesteps 20000 --exp_name "test_5p_dicl_s_clean_baseline_27_sep_with_profiling" --batch_size 256 --llm_batch_size 7 --llm_learning_frequency 256 --context_length 500 --interact_every 1 --learning_starts 5000 --llm_learning_starts 10000 --llm_model 'meta-llama/Llama-3.2-1B' --method 'dicl_s_pca'


echo "Job ended at: $(date)"

