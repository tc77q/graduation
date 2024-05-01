from rl_zoo3.train import train
import warnings
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
warnings.filterwarnings("ignore",category=DeprecationWarning)
if __name__ == "__main__":
    train()
