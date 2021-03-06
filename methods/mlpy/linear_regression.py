'''
  @file linear_regression.py
  @author Marcus Edel, Anand Soni

  Linear Regression with mlpy.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

#Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from timer import *
from definitions import *
from misc import *

import numpy as np
import mlpy

'''
This class implements the Linear Regression benchmark.
'''
class LinearRegression(object):

  '''
  Create the Linear Regression benchmark instance.

  @param dataset - Input dataset to perform Linear Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None

  '''
  Build the model for the Linear Regression.

  @param data - The train data.
  @param responses - The responses for the training set.
  @return The created model.
  '''
  def BuildModel(self, data, responses):
    # Create and train the classifier.
    model = mlpy.OLS()
    model.learn(data, responses)
    return model

  '''
  Use the mlpy libary to implement Linear Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LinearRegressionMlpy(self, options):
    def RunLinearRegressionMlpy(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) >= 2:
        test_data = np.genfromtxt(self.dataset[1], delimiter=',')

      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset[0])

      try:
        with totalTimer:
          # Perform linear regression.
          model = mlpy.OLS()
          model.learn(X, y)
          b =  model.beta()

          if len(self.dataset) >= 2:
            #prediction on the test data.
            pred = model.pred(test_data)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      if len(self.dataset) >= 2:
        np.savetxt("mlpy_lr_predictions.csv", pred, delimiter="\n")

      return time

    return timeout(RunLinearRegressionMlpy, self.timeout)

  '''
  Run all the metrics for the classifier.
  '''
  def RunMetrics(self, options):
    if len(self.dataset) >= 2:

      # Check if we need to build and run the model.
      if not CheckFileAvailable('mlpy_lr_predictions.csv'):
        self.RunTiming(options)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      predictedlabels = LoadDataset("mlpy_lr_predictions.csv")

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      AvgAcc = Metrics.AverageAccuracy(confusionMatrix)
      AvgPrec = Metrics.AvgPrecision(confusionMatrix)
      AvgRec = Metrics.AvgRecall(confusionMatrix)
      AvgF = Metrics.AvgFMeasure(confusionMatrix)
      AvfLift = Metrics.LiftMultiClass(confusionMatrix)
      AvgMCC = Metrics.MCCMultiClass(confusionMatrix)
      AvgInformation = Metrics.AvgMPIArray(confusionMatrix, truelabels, predictedlabels)
      SimpleMSE = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)
      metrics_dict = {}
      metrics_dict['Avg Accuracy'] = AvgAcc
      metrics_dict['MultiClass Precision'] = AvgPrec
      metrics_dict['MultiClass Recall'] = AvgRec
      metrics_dict['MultiClass FMeasure'] = AvgF
      metrics_dict['MultiClass Lift'] = AvgLift
      metrics_dict['MultiClass MCC'] = AvgMCC
      metrics_dict['MultiClass Information'] = AvgInformation
      metrics_dict['Simple MSE'] = SimpleMSE
      return metrics_dict
    else:
      Log.Fatal("This method requires three datasets.")

  '''
  Perform Linear Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform Linear Regression.", self.verbose)

    return self.LinearRegressionMlpy(options)
