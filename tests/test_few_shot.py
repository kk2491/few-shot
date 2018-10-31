import unittest
from torch.utils.data import DataLoader

from few_shot.few_shot import compute_prototypes, NShotSampler
from few_shot.datasets import DummyDataset, OmniglotDataset, MiniImageNet
from few_shot.models import get_few_shot_encoder


class TestProtoNets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = DummyDataset(samples_per_class=1000, n_classes=20)

    def test_compute_prototypes(self):
        # test prototypes are computed correctly on dummy dataset
        n, k, q = 2, 4, 3
        n_shot_taskloader = DataLoader(self.dataset,
                                       batch_sampler=NShotSampler(self.dataset, 100, n, k, q))

        # Load a single n-shot task and compute prototypes
        for x, y in n_shot_taskloader:
            support = x[:n * k]
            support_labels = y[:n*k]
            prototypes = compute_prototypes(support, k, n)

            # By construction the second feature of samples from the
            # DummyDataset is equal to the label.
            # As class prototypes are constructed from the means of the support
            # set items of a particular class the value of the second feature
            # of the class prototypes should be equal to the label of that class.
            for i in range(k):
                self.assertEqual(
                    support_labels[i * n],
                    prototypes[i, 1],
                    'Prototypes computed incorrectly!'
                )

            break

    def test_create_model(self):
        # Check output of encoder has shape specified in paper
        encoder = get_few_shot_encoder(num_input_channels=1).float()
        omniglot = OmniglotDataset('background')
        self.assertEqual(
            encoder(omniglot[0][0].unsqueeze(0).float()).shape[1],
            64,
            'Encoder network should produce 64 dimensional embeddings on Omniglot dataset.'
        )

        encoder = get_few_shot_encoder(num_input_channels=3).float()
        omniglot = MiniImageNet('background')
        self.assertEqual(
            encoder(omniglot[0][0].unsqueeze(0).float()).shape[1],
            1600,
            'Encoder network should produce 1600 dimensional embeddings on miniImageNet dataset.'
        )

