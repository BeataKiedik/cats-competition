#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kickstarted on Tuesday, 3rd of April, 2018.

This main script provides the backbone for the machine learning algorithm(s) and sets the framework for the validation-scheme.
Recommended Python interpreter is of version >=3.5.
Three-state classification into HER2+, TN or HR+.
Evaluation metric should be accuracy.
"""

# IMPORT OF LIBRARIES
import time
import numpy as np
import matplotlib.pyplot as plt
import sklearn as skl
import pandas as pd
import math
import sys
from termcolor import colored

# CONSTANTS
from classifiers.dnn_classifier import DeepNeuralClassifier

START_TIME = time.time()
BEANS_CONSTANT = 69
N_SAMPLES = 100  # number of samples (patients)
N_VARIABLES = 2834  # number of chromosomal locations
OUTER_FOLD = 4  # OUTER_FOLD-fold CV (outer loop) for triple-CV (Wessels, 2005: 3-fold)
INNER_FOLD = 5  # INNER_FOLD-fold CV (inner loop) for triple-CV (Wessels, 2005: 10-fold)

CLASSIFIERS = {
    'dnn': DeepNeuralClassifier
}


def get_data():
    """
    Import of raw data as np.array using Pandas.

    import of train_clinical.txt, samples x 2 (sample name, label)
    Sample example (100 in total, sample name): 'Array.129'
    Subgroups (3 in total, label): 'HER2+', 'HR+' and 'Triple Neg'
    :return: train_clinical, train_call
    """
    #
    train_clinical = pd.read_csv('data/Train_clinical.txt', sep='\t').values
    print('Data set "train_clinical" was loaded (%i rows and %i cols).' % (
        train_clinical.shape[0], train_clinical.shape[1]))

    # import and transpose of train_call.txt, samples x variables
    train_call = np.transpose(
        pd.read_csv('data/Train_call.txt', sep='\t', usecols=range(4, 4 + N_SAMPLES)).values.astype('float32'))
    print('Data set "train_call" was loaded (%i rows and %i cols).' % (train_call.shape[0], train_call.shape[1]))

    return train_call, train_clinical


def cross_validate(model, features, labels):
    """
    Performs triple cross-validation, using accuracy as evaluation metric
    :param model:
    :param features: An MxN matrix of features to use in prediction
    :param labels: An N row list of labels to predict
    :return: training_accuracy, training_accuracy_mean, validation_accuracy, validation_accuracy_mean
    """
    train_accuracy, val_accuracy = [], []
    chunk_size = int(N_SAMPLES / OUTER_FOLD)  # number of samples provided after first split
    val_size = int(N_SAMPLES / OUTER_FOLD / INNER_FOLD)  # number of samples provided after second split

    # Select chunk_size amount of rows (indices) randomly from the data for every outer round
    for indices in [np.random.choice(len(features), chunk_size) for _ in range(OUTER_FOLD)]:
        inner_train_accuracy, inner_val_accuracy = [], []
        for _ in range(INNER_FOLD):
            np.random.shuffle(indices)  # Reshuffle to get a different training/validation set every inner round
            train_features = np.asarray([features[index] for index in indices[val_size:]])
            train_labels = np.asarray([labels[index] for index in indices[val_size:]])
            val_features, val_labels = np.asarray(features[indices[0:val_size]]), np.asarray(labels[indices[0:val_size]])

            # Train the model on the current round's training set, and predict the current round's validation set
            train_accuracy.append(model.train(train_features, train_labels))
            val_accuracy.append(model.predict(val_features, val_labels))

    return train_accuracy, np.mean(train_accuracy), val_accuracy, np.mean(val_accuracy)

def plot_accuracy(model, train_accuracy, train_accuracy_mean, val_accuracy, val_accuracy_mean):
    """
    Plots the accuracies of all rounds of a triple cross validation
    :param train_accuracy:
    :param val_accuracy:
    :return:
    """
    print('Training accuracy: %.4f.' % train_accuracy_mean)
    print(colored('Validation accuracy: %.4f.', 'green') % val_accuracy_mean + " You 'mirin, bra?")
    print('The distribution of the evaluation metric (accuracy) is being plotted.')

    plt.figure()
    plt.plot(train_accuracy, alpha=0.4, label='training accuracies')
    plt.plot(val_accuracy, alpha=0.4, label='validation accuracies')
    plt.xlabel('Cross-validation round')
    plt.ylabel('Accuracy')
    plt.title('Distribution of accuracies in three-fold CV for %s' % model.__class__.__name__)
    plt.legend()
    plt.show()

def main():
    print('Script execution was initiated.')

    # Setting the seed (for reproducibility of training results)
    np.random.seed(0)

    # The order in both np.arrays is the same as in the original files, which means that the label (output) \\
    # train_clinical[a, 1] is the wanted prediction for the data (features) in train_call[a, :]"""
    train_call, train_clinical = get_data()
    features, labels = train_call, train_clinical[:, 1]

    if len(features) != len(labels):
        sys.exit('Data and response files do not have the same amount of lines')

    # TODO: Data pre-processing and feature selection

    # Triple cross-validation (with random sampling without replacement) (similar to Wessels, 2005)
    # Hyper-parameter selection can be integrated (e. g. k in kNN)
    # (ALTERNATIVE: WITH REPLACEMENT, then other OUTER_FOLD AND INNER_FOLD are allowed)
    # test if provided constants INNER_FOLD and OUTER_FOLD are allowed
    if not (N_SAMPLES % OUTER_FOLD == 0 and N_SAMPLES / OUTER_FOLD % INNER_FOLD == 0):
        print('INNER_FOLD and OUTER_FOLD constants are not appropriate.')
        print('Script execution is aborted after %.8s s.' % (time.time() - START_TIME))
        sys.exit()

    if len(sys.argv) != 2 or sys.argv[1] not in CLASSIFIERS.keys():
        sys.exit('Usage: python main.py [%s]' % '|'.join(CLASSIFIERS.keys()))

    # Select model to run, based on command line parameter
    feature_length, num_unique_labels = features.shape[1], len(set(labels))
    model = CLASSIFIERS[sys.argv[1]](feature_length, num_unique_labels)

    # give standard output
    print('Triple cross-validation with %i-fold and subsequent %i-fold split is initiated.' % (OUTER_FOLD, INNER_FOLD))

    train_accuracy, train_accuracy_mean, val_accuracy, val_accuracy_mean = cross_validate(model, features, labels)

    print('Triple-CV was finished.')
    plot_accuracy(model, train_accuracy, train_accuracy_mean, val_accuracy, val_accuracy_mean)

    # TODO: Save model as *.pkl USING sklearn.joblib() ?


# EXECUTION
if __name__ == '__main__':
    main()
    print('\nFinished: The script was successfully executed in %.8s s.' % (time.time() - START_TIME))