import os
os.environ['NETLENS_BACKEND'] = 'tensorflow'

from tensorflow.keras.layers import Activation, Dense, Input
from tensorflow.keras.models import Model
from unittest import TestCase, main

from netlens.models import ModelWrapper
from tests.unit.attribution_axioms_test_base import AxiomsTestBase

from netlens import backend as B
from netlens.attribution import InternalInfluence
from netlens.distributions import LinearDoi
from netlens.quantities import ClassQoI
from netlens.slices import InputCut


class AxiomsTest(AxiomsTestBase, TestCase):

    def setUp(self):
        super(AxiomsTest, self).setUp()

        # Make a linear model for testing.
        x_lin = Input((self.input_size,))
        y_lin = Dense(self.output_size)(x_lin)

        self.model_lin = ModelWrapper(Model(x_lin, y_lin))

        self.model_lin._model.set_weights([
            self.model_lin_weights, self.model_lin_bias])

        # Make a deeper model for testing.
        x_deep = Input((self.input_size,))
        y_deep = Dense(self.internal1_size)(x_deep)
        y_deep = Activation('relu')(y_deep)
        y_deep = Dense(self.internal2_size)(y_deep)
        y_deep = Activation('relu')(y_deep)
        y_deep = Dense(self.output_size)(y_deep)

        self.model_deep = ModelWrapper(Model(x_deep, y_deep))

        self.model_deep._model.set_weights([
            self.model_deep_weights_1, self.model_deep_bias_1,
            self.model_deep_weights_2, self.model_deep_bias_2,
            self.model_deep_weights_3, self.model_deep_bias_3])

        self.layer2 = 2
        self.layer3 = 3


    def test_data_tensor_compatibility(self):
        c = 2
        infl = InternalInfluence(
            self.model_deep, 
            InputCut(), 
            ClassQoI(c), 
            LinearDoi(self.baseline, resolution=100), 
            multiply_activation=True)
 
        res = infl.attributions(B.as_tensor(self.x))

        self.assertTrue(isinstance(res, B.Tensor))


if __name__ == '__main__':
    main()