import gym
from stable_baselines3 import PPO
import os

models_dir = 'models/PPO'
models_env = 'LunarLander-v2'
models_alg = 'dqn'
model_path = f'{"rl-trained-agents"}/{models_alg}/{models_env}_1/{models_env}.zip'
print(model_path)
env = gym.make('LunarLander-v2')
# env.reset()
#
# model = PPO.load(model_path, env=env)
#
# episodes = 10
# for ep in range(episodes):
#     obs = env.reset()
#     while True:
#         action, _states = model.predict(obs)
#         obs, rewards, done, info = env.step(action)
#         if done:
#             break
# env.close()