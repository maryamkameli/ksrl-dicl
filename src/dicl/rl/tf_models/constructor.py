import numpy as np
import tensorflow as tf

from ..tf_models.fc import FC
from ..tf_models.bnn import BNN

def construct_model(obs_dim, act_dim, hidden_dim=200, num_networks=1, num_elites=1, session=None):
	print('[ BNN ] Observation dim {} | Action dim: {} | Hidden dim: {}'.format(obs_dim, act_dim, hidden_dim))
	params = {'name': 'BNN', 'num_networks': num_networks, 'num_elites': num_elites, 'sess': session}
	model = BNN(params)

	model.add(FC(hidden_dim, input_dim=obs_dim+act_dim, activation="swish", weight_decay=0.00025))
	model.add(FC(hidden_dim, activation="swish", weight_decay=0.0005))
	model.add(FC(hidden_dim, activation="swish", weight_decay=0.0005))
	model.add(FC(2*(obs_dim+act_dim), activation="swish", weight_decay=0.00075))
	model.add(FC(obs_dim, weight_decay=0.00075))
	model.finalize(tf.train.AdamOptimizer, {"learning_rate": 0.001})
	return model

def construct_cost_model(obs_dim, act_dim, hidden_dim=200, num_networks=1, num_elites=1, session=None):
	print('[ BNN ] Observation dim {} | Action dim: {} | Hidden dim: {}'.format(obs_dim, act_dim, hidden_dim))
	params = {'name': 'BNN_cost', 'num_networks': num_networks, 'num_elites': num_elites, 'sess': session}
	model = BNN(params)

	model.add(FC(hidden_dim, input_dim=obs_dim+act_dim, activation="swish", weight_decay=0.00025))
	model.add(FC(hidden_dim, activation="swish", weight_decay=0.0005))
	model.add(FC(hidden_dim, activation="swish", weight_decay=0.0005))
	model.add(FC(2*(obs_dim+act_dim), activation="swish", weight_decay=0.00075))
	model.add(FC(1, weight_decay=0.00075))
	model.finalize(tf.train.AdamOptimizer, {"learning_rate": 0.001})
	return model

def construct_shallow_model(obs_dim, act_dim, hidden_dim=200, num_networks=1, num_elites=1, session=None):
	print('[ BNN ] Observation dim {} | Action dim: {} | Hidden dim: {}'.format(obs_dim, act_dim, hidden_dim))
	params = {'name': 'BNN', 'num_networks': num_networks, 'num_elites': num_elites, 'sess': session}
	model = BNN(params)

	model.add(FC(hidden_dim, input_dim=obs_dim+act_dim, activation="swish", weight_decay=0.000025))
	model.add(FC(hidden_dim, activation="swish", weight_decay=0.00005))
	# model.add(FC(hidden_dim, activation="swish", weight_decay=0.0005))
	model.add(FC(2*(obs_dim+act_dim), activation="swish", weight_decay=0.000075))
	model.add(FC(obs_dim, weight_decay=0.000075))
	model.finalize(tf.compat.v1.train.AdamOptimizer, {"learning_rate": 0.001})
	return model

def construct_shallow_cost_model(obs_dim, act_dim, hidden_dim=200, num_networks=1, num_elites=1, session=None):
	print('[ BNN ] Observation dim {} | Action dim: {} | Hidden dim: {}'.format(obs_dim, act_dim, hidden_dim))
	params = {'name': 'BNN_cost', 'num_networks': num_networks, 'num_elites': num_elites, 'sess': session}
	model = BNN(params)

	model.add(FC(hidden_dim, input_dim=obs_dim+act_dim, activation="swish", weight_decay=0.000025))
	model.add(FC(hidden_dim, activation="swish", weight_decay=0.00005))
	# model.add(FC(hidden_dim, activation="swish", weight_decay=0.0005))
	model.add(FC(2*(obs_dim+act_dim), activation="swish", weight_decay=0.000075))
	model.add(FC(1, weight_decay=0.000075))
	model.finalize(tf.train.AdamOptimizer, {"learning_rate": 0.001})
	return model

def format_samples_for_training(samples):
	obs = samples['observations']
	act = samples['actions']
	next_obs = samples['next_observations']
	rew = samples['rewards']
	delta_obs = next_obs - obs
	inputs = np.concatenate((obs, act), axis=-1)
	outputs = np.concatenate((rew, delta_obs), axis=-1)
	return inputs, outputs

def reset_model(model):
	model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=model.name)
	model.sess.run(tf.initialize_vars(model_vars))

if __name__ == '__main__':
	model = construct_model()
