import pandas as pdfrom keras.models import Sequentialfrom keras.layers import Dense, Dropout, BatchNormalizationfrom scikeras.wrappers import KerasRegressorfrom sklearn.model_selection import cross_val_scorefrom sklearn.model_selection import KFoldfrom sklearn.preprocessing import StandardScalerfrom sklearn.pipeline import Pipelineimport numpy as npimport GPyimport matplotlib.pyplot as pltimport osos.chdir("/Users/dawr2/Desktop/Ranadeep_Daw_Projects/SBOOOST")## Read PM2.5 data at June 05, 2019df1 = pd.read_csv('DeepKriging-master/covariate0605.csv')df2 = pd.read_csv('DeepKriging-master/pm25_0605.csv')covariates = df1.values[:,3:]aqs_lonlat=df2.values[:,[1,2]]from scipy import spatialnear = df1.values[:,[1,2]]tree = spatial.KDTree(list(zip(near[:,0].ravel(), near[:,1].ravel())))tree.dataidx = tree.query(aqs_lonlat)[1]df2_new = df2.assign(neighbor = idx)df_pm25 = df2_new.groupby('neighbor')['PM25'].mean()df_pm25_class = pd.cut(df_pm25,bins=[0,12.1,35.5],labels=[0,1])idx_new = df_pm25.index.valuespm25 = df_pm25.valuespm25_class = np.array(df_pm25_class.values)z = pm25[:,None]z_class = pm25_class[:,None]lon = df1.values[:,1]lat = df1.values[:,2]normalized_lon = (lon-min(lon))/(max(lon)-min(lon))normalized_lat = (lat-min(lat))/(max(lat)-min(lat))N = lon.shape[0]num_basis = [10**2,19**2,37**2]knots_1dx = [np.linspace(0,1,int(np.sqrt(i))) for i in num_basis]knots_1dy = [np.linspace(0,1,int(np.sqrt(i))) for i in num_basis]##Wendland kernelbasis_size = 0phi = np.zeros((N, sum(num_basis)))for res in range(len(num_basis)):    theta = 1/np.sqrt(num_basis[res])*2.5    knots_x, knots_y = np.meshgrid(knots_1dx[res],knots_1dy[res])    knots = np.column_stack((knots_x.flatten(),knots_y.flatten()))    for i in range(num_basis[res]):        d = np.linalg.norm(np.vstack((normalized_lon,normalized_lat)).T-knots[i,:],axis=1)/theta        for j in range(len(d)):            if d[j] >= 0 and d[j] <= 1:                phi[j,i + basis_size] = (1-d[j])**6 * (35 * d[j]**2 + 18 * d[j] + 3)/3            else:                phi[j,i + basis_size] = 0    basis_size = basis_size + num_basis[res] ## Romove the all-zero columnsidx_zero = np.array([], dtype=int)for i in range(phi.shape[1]):    if sum(phi[:,i]!=0)==0:        idx_zero = np.append(idx_zero,int(i))phi_reduce = np.delete(phi,idx_zero,1)print(phi.shape)print(phi_reduce.shape)phi_obs = phi_reduce[idx_new,:]s_obs = np.vstack((normalized_lon[idx_new],normalized_lat[idx_new])).TX = covariates[idx_new,:]normalized_X = Xfor i in range(X.shape[1]):    normalized_X[:,i] = (X[:,i]-min(X[:,i]))/(max(X[:,i])-min(X[:,i]))N_obs = X.shape[0]# scatter plot of the circles dataset with points colored by classfrom numpy import wherefrom matplotlib import pyplot# select indices of points with each class labelfor i in range(2):	samples_ix = where(z_class[:,0] == i)	pyplot.scatter(s_obs[samples_ix, 0], s_obs[samples_ix, 1], label=str(i))pyplot.legend()pyplot.show()#pyplot.scatter(s_obs[:, 0], s_obs[:, 1], c=targets)pyplot.scatter(df1.long, df1.lat, c=df1.temp)pyplot.xlabel("Long")pyplot.ylabel("Lat")pyplot.title("Heatmap of Temperature")pyplot.savefig("temp.png")pyplot.scatter(df1.long, df1.lat, c=df1.pres)pyplot.xlabel("Long")pyplot.ylabel("Lat")pyplot.title("Heatmap of Pressure")pyplot.savefig("pres.png")pyplot.scatter(df2.Longitude, df2.Latitude, c=df2.PM25, s =5)pyplot.xlabel("Long")pyplot.ylabel("Lat")pyplot.title("Heatmap of PM2.5")pyplot.savefig("pm25.png")import xgboost as xgbfrom sklearn.model_selection import train_test_split # Create regression matricesinputs = np.hstack((normalized_X,phi_obs))#inputs = phi_obstargets = ztargets_class = z_classX_train, X_test, y_train, y_test = train_test_split(inputs, targets,                                    random_state=104,                                     test_size=0.25,                                     shuffle=True) dtrain_reg = xgb.DMatrix(X_train, y_train, enable_categorical=True)dtest_reg  = xgb.DMatrix(X_test, y_test, enable_categorical=True)# Define hyperparametersparams = {"objective": "reg:squarederror",          "max_depth": 5}evals = [(dtrain_reg, "train"), (dtest_reg, "validation")]n = 5000model = xgb.train(   params=params,   dtrain=dtrain_reg,   num_boost_round=n,   evals=evals,   verbose_eval=10,   # Activate early stopping   early_stopping_rounds=100)results = xgb.cv(   params, dtrain_reg,   num_boost_round=n,   nfold=50,   early_stopping_rounds=20)from sklearn.metrics import mean_squared_errorpreds = model.predict(dtest_reg)plt.scatter(preds, y_test)