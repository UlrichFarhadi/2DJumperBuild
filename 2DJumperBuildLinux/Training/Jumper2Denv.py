from ensurepip import version
from os import times

import sys
import gym
import time
import numpy as np
import torch

import GA_evolver

# Create an instance from the class GA_evolver
from random import random

import mlagents
from mlagents_envs.environment import ActionTuple, BaseEnv
from mlagents_envs.environment import UnityEnvironment as UE
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel


def create_env(show_graphics=False, env_simulation_speed=1.0):
    channel = EngineConfigurationChannel()
    env = UE(file_name='2DJumperBuild/2DJumperBuildLinux/2DJumperBuildLinux.x86_64', seed=1, side_channels=[channel], no_graphics=not show_graphics)
    channel.set_configuration_parameters(time_scale = env_simulation_speed)
    print("Resetting environment")
    env.reset()
    print("Environment has been reset")
    behavior_name = list(env.behavior_specs)[0]
    print(f"Name of the behavior : {behavior_name}")
    spec = env.behavior_specs[behavior_name]

    print("Number of observations : ", len(spec.observation_specs))

    if spec.action_spec.is_continuous():
        print(f"There are {spec.action_spec.continuous_size} continuous actions")
    if spec.action_spec.is_discrete():
        print(f"There are {spec.action_spec.discrete_size} discrete actions")
    
    return env, behavior_name

def run_one_episode(env, model, behavior_name, timesteps_per_episode=1000):
    # Environment runsin 50 fps, so 1 timestep equals to 1 frame
    def reward_function(obs, goal_radius, timesteps, time_alive_reward=1.0, goal_reached_reward=2.0, agent_fell_over_reward=-1.0):
        terminate = False # Give signal to terminate episode
        reward = 0

        # Give reward for:
        # - If agent fell over give negative reward (agent_fell_over_reward) and terminate
        angle = obs[2]
        if angle <= 90:
            if angle > 70:
                reward += agent_fell_over_reward
                terminate = True
        else:
            if angle < 290:
                reward += agent_fell_over_reward
                terminate = True
        # - If agent is closer than goal_radius to the goal (aka goal reached) give a reward of goal_reached_reward and terminate
        agent_yz = np.array((obs[0], obs[1]))
        goal_yz = np.array((obs[5], obs[6]))
        dist = np.linalg.norm(agent_yz - goal_yz)
        if dist <= goal_radius:
            reward += goal_reached_reward
            terminate = True

        if timesteps == timesteps_per_episode - 1:  # Episode time limited reached, give full reward
            terminate = True
        
        if terminate: # If terminate: Give reward between 0 and time_alive_reward depending on how long it was alive compared to the total timesteps_per_episode
            reward += (timesteps / (timesteps_per_episode - 1)) * time_alive_reward

        return reward, terminate

    cum_reward = 0
    tracked_agent = -1 # -1 indicates not yet tracking

    for timesteps in range(timesteps_per_episode):
        # Take a step
        env.step()
        # Move the simulation forward
        decision_steps, terminal_steps = env.get_steps(behavior_name)

        if tracked_agent == -1 and len(decision_steps) >= 1:
            tracked_agent = decision_steps.agent_id[0]
        if len(decision_steps) == 0:
            continue 

        # // Observations, size = 8
        # // [0] -> Agent y position
        # // [1] -> Agent z position
        # // [2] -> Agent x euler angle (aka slope
        # // [3] -> Agent y velocity
        # // [4] -> Agent z veloity
        # // [5] -> Goal y position
        # // [6] -> Goal z position
        # // [7] -> Spring contraction distance
        obs = decision_steps.obs[tracked_agent][0]

        # // Actions, size = 3
        # // [0] -> Right rotor aka rotor1
        # // [1] -> Left rotor aka rotor3
        # // [2] -> Spring contraction
        action = model(torch.from_numpy(obs))
        
        # Determine rewards
        reward, terminate = reward_function(obs, goal_radius=2.0, timesteps=timesteps, time_alive_reward=1.0, goal_reached_reward=2.0, agent_fell_over_reward=-1.0)
        cum_reward += reward
        if terminate:
            break

        # Set the actions
        action = action.cpu().detach().numpy()
        action = action.reshape(1,3)
        
        acton_tuple = ActionTuple()
        acton_tuple.add_continuous(action)
        #ac = spec.action_spec.random_action(len(decision_steps))
        env.set_action_for_agent(behavior_name, tracked_agent, acton_tuple)

    return cum_reward

