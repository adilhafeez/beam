#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""End-to-End test for Sklearn Inference"""

import logging
import unittest
import uuid

import pytest

from apache_beam.examples.inference import sklearn_mnist_classification
from apache_beam.io.filesystems import FileSystems
from apache_beam.testing.test_pipeline import TestPipeline


def process_outputs(filepath):
  with FileSystems().open(filepath) as f:
    lines = f.readlines()
  lines = [l.decode('utf-8').strip('\n') for l in lines]
  return lines


@pytest.mark.skip
@pytest.mark.uses_sklearn
@pytest.mark.it_postcommit
class SklearnInference(unittest.TestCase):
  def test_sklearn_mnist_classification(self):
    test_pipeline = TestPipeline(is_integration_test=False)
    input_file = 'gs://apache-beam-ml/testing/inputs/it_mnist_data.csv'
    output_file_dir = 'gs://temp-storage-for-end-to-end-tests'
    output_file = '/'.join([output_file_dir, str(uuid.uuid4()), 'result.txt'])
    model_path = 'gs://apache-beam-ml/models/mnist_model_svm.pickle'
    extra_opts = {
        'input': input_file,
        'output': output_file,
        'model_path': model_path,
    }
    sklearn_mnist_classification.run(
        test_pipeline.get_full_options_as_args(**extra_opts),
        save_main_session=False)
    self.assertEqual(FileSystems().exists(output_file), True)

    expected_output_filepath = 'gs://apache-beam-ml/testing/expected_outputs/test_sklearn_mnist_classification_actuals.txt'  # pylint: disable=line-too-long
    expected_outputs = process_outputs(expected_output_filepath)

    predicted_outputs = process_outputs(output_file)
    self.assertEqual(len(expected_outputs), len(predicted_outputs))

    predictions_dict = {}
    for i in range(len(predicted_outputs)):
      true_label, prediction = predicted_outputs[i].split(',')
      predictions_dict[true_label] = prediction

    for i in range(len(expected_outputs)):
      true_label, expected_prediction = expected_outputs[i].split(',')
      self.assertEqual(predictions_dict[true_label], expected_prediction)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.DEBUG)
  unittest.main()