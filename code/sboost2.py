#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 13:17:56 2024

@author: dawr2

"""


from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold

subsample = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
colsample_bytree = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
param_grid = dict(subsample=subsample, colsample_bytree=colsample_bytree)
model = XGBRegressor()
kfold = KFold(n_splits=10, shuffle=True, random_state=7)
grid_search = GridSearchCV(model, param_grid, scoring="neg_mean_absolute_error", n_jobs=-1, cv=kfold)


grid_result = grid_search.fit(inputs, targets)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))

means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
	print("%f (%f) with: %r" % (-mean, stdev, param))
# plot




pyplot.errorbar(subsample, means, yerr=stds)
pyplot.title("XGBoost subsample vs Log Loss")
pyplot.xlabel('subsample')
pyplot.ylabel('Log Loss')

best = grid_search.best_estimator_
preds = best.predict(inputs)


pyplot.scatter(s_obs[:,0], s_obs[:,1], c=preds, s =5)
pyplot.xlabel("Long")
pyplot.ylabel("Lat")
pyplot.title("Prediction of PM2.5")
pyplot.savefig("pm25_pred.png")
