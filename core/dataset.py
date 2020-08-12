import torch
from torch.utils.data import Dataset, DataLoader

from . import task
from . import tools


class TaskDataset(Dataset):

    def __init__(self, rule_name, hp, mode='train', is_cuda=False, **kwargs):
        '''provide name of the rules'''
        self.rule_name = rule_name

        self.hp = hp

        self.is_cuda = is_cuda

        if mode == 'train':
            self.bach_size = hp['batch_size_train']
            self.task_mode = 'random'
        elif mode == 'test':
            self.bach_size = hp['batch_size_test']
            self.task_mode = 'random_validate'
        elif mode == 'test_generalize':
            self.bach_size = hp['batch_size_test']
            self.task_mode = 'test_generalize'
        else:
            raise ValueError('Unknown mode: ' + str(mode))

        self.counter = 0
        self.kwargs = kwargs

    def __len__(self):
        '''arbitrary'''
        return 10000000

    def __getitem__(self, index):

        self.trial = task.generate_trials(self.rule_name, self.hp, self.task_mode, batch_size=self.bach_size, **self.kwargs)

        '''model.x: trial.x,
                 model.y: trial.y,
                 model.cost_mask: trial.cost_mask,
                 model.seq_len: trial.seq_len,
                 model.initial_state: np.zeros((trial.x.shape[1], hp['n_rnn']))'''

        result = dict()
        result['inputs'] = torch.as_tensor(self.trial.x)
        result['target_outputs'] = torch.as_tensor(self.trial.y)
        result['cost_mask'] = torch.as_tensor(self.trial.cost_mask)
        result['cost_start_time'] = 0 # trial.cost_start_time
        result['cost_end_time'] = self.trial.max_seq_len
        result['seq_mask'] = tools.sequence_mask(self.trial.seq_len)
        result['initial_state'] = torch.zeros((self.trial.x.shape[1], self.hp['n_rnn']))

        result['epochs'] = self.trial.epochs
        # basic timing tasks
        if self.rule_name == 'interval_production':
            result['prod_interval'] = self.trial.prod_interval
            result['dly_interval'] = self.trial.dly_interval
        elif self.rule_name == 'interval_comparison':
            result['prod_interval1'] = self.trial.prod_interval1
            result['prod_interval2'] = self.trial.prod_interval2
            result['dly_interval'] = self.trial.dly_interval
        # combined timing tasks
        elif self.rule_name == 'timed_spatial_reproduction':
            result['prod_interval'] = self.trial.prod_interval
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center'] = self.trial.gaussian_center
        elif self.rule_name == 'timed_spatial_reproduction_broad_tuning':
            result['prod_interval'] = self.trial.prod_interval
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center'] = self.trial.gaussian_center
        elif self.rule_name == 'timed_decision_making':
            result['prod_interval'] = self.trial.prod_interval
            result['dly_interval'] = self.trial.dly_interval
            result['strength1'] = self.trial.strength1
            result['strength2'] = self.trial.strength2
        # non-timing tasks
        elif self.rule_name == 'spatial_reproduction':
            result['prod_interval'] = self.trial.prod_interval
            result['gaussian_center'] = self.trial.gaussian_center
        elif self.rule_name == 'spatial_reproduction_broad_tuning':
            result['prod_interval'] = self.trial.prod_interval
            result['gaussian_center'] = self.trial.gaussian_center
        elif self.rule_name == 'spatial_reproduction_variable_delay':
            result['prod_interval'] = self.trial.prod_interval
            result['gaussian_center'] = self.trial.gaussian_center

        elif self.rule_name == 'spatial_comparison':
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center1'] = self.trial.gaussian_center1
            result['gaussian_center2'] = self.trial.gaussian_center2
        elif self.rule_name == 'spatial_comparison_broad_tuning':
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center1'] = self.trial.gaussian_center1
            result['gaussian_center2'] = self.trial.gaussian_center2
        elif self.rule_name == 'spatial_comparison_variable_delay':
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center1'] = self.trial.gaussian_center1
            result['gaussian_center2'] = self.trial.gaussian_center2

        elif self.rule_name == 'spatial_change_detection':
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center1'] = self.trial.gaussian_center1
            result['gaussian_center2'] = self.trial.gaussian_center2
        elif self.rule_name == 'spatial_change_detection_broad_tuning':
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center1'] = self.trial.gaussian_center1
            result['gaussian_center2'] = self.trial.gaussian_center2
        elif self.rule_name == 'spatial_change_detection_variable_delay':
            result['dly_interval'] = self.trial.dly_interval
            result['gaussian_center1'] = self.trial.gaussian_center1
            result['gaussian_center2'] = self.trial.gaussian_center2

        elif self.rule_name == 'decision_making':
            result['prod_interval'] = self.trial.prod_interval
            result['strength1'] = self.trial.strength1
            result['strength2'] = self.trial.strength2

        elif self.rule_name == 'decision_making_variable_delay':
            result['prod_interval'] = self.trial.prod_interval
            result['strength1'] = self.trial.strength1
            result['strength2'] = self.trial.strength2

        elif self.rule_name == 'ctx_decision_making':
            result['prod_interval'] = self.trial.prod_interval
            result['strength1'] = self.trial.strength1
            result['strength2'] = self.trial.strength2
            result['choice'] = self.trial.choice
        elif self.rule_name == 'ctx_decision_making_variable_delay':
            result['prod_interval'] = self.trial.prod_interval
            result['strength1'] = self.trial.strength1
            result['strength2'] = self.trial.strength2
            result['choice'] = self.trial.choice

        return result


class TaskDatasetForRun(object):

    def __init__(self, rule_name, hp, noise_on=True, mode='test', **kwargs):
        '''provide name of the rules'''
        self.rule_name = rule_name
        self.hp = hp
        self.kwargs = kwargs
        self.noise_on = noise_on

        self.mode = mode

    def __getitem__(self):

        self.trial = task.generate_trials(self.rule_name, self.hp, self.mode, noise_on=self.noise_on, **self.kwargs)

        result = dict()
        result['inputs'] = torch.as_tensor(self.trial.x)
        result['target_outputs'] = torch.as_tensor(self.trial.y)
        result['cost_mask'] = torch.as_tensor(self.trial.cost_mask)
        result['cost_start_time'] = 0 # trial.cost_start_time
        result['cost_end_time'] = self.trial.max_seq_len
        result['seq_mask'] = tools.sequence_mask(self.trial.seq_len)
        result['initial_state'] = torch.zeros((self.trial.x.shape[1], self.hp['n_rnn']))

        return result


