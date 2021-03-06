#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 12:43:48 2018

@author: Brettmccausland
"""
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import operator
from operator import itemgetter, attrgetter
from sklearn.preprocessing import Imputer
from sklearn.cross_validation import train_test_split

#precondiotion:
#postcondition:
def minkowskiDist(list_R,list_Rn,p):
  sum=0
  count=len(list_R)
  for i in range(count):
    sum = sum + pow((abs(list_R[i]-list_Rn[i])),p)
  fp= 1/p
  return pow(sum,fp)

#precondiotion:
#postcondition:
def assignClassification(df_centroids,df_Xinput):


 numCentroids=df_centroids.shape[0]
 numRows=df_Xinput.shape[0]
 list_clusterAssignmets=[0] * numRows
 list_tuple_dist=[]


 for row in range(numRows):
   for k in range(numCentroids):
     dist= minkowskiDist(list(df_centroids.iloc[k]),list(df_Xinput.iloc[row]),2)
     list_tuple_dist.append([dist,k])
   list_tuple_dist.sort(key=operator.itemgetter(0))
   tuple_best=list_tuple_dist[0]
   list_clusterAssignmets[row]=tuple_best[1]
   list_tuple_dist.clear()
 return list_clusterAssignmets


#precondiotion:
#  list_clusterAssign: initialized with class assignments for df_Xinput
#  list_clusterAssign is used to map to correct centroid
#  df_Xinput: contains the feature matrix
#postcondition:
#   returns a dataframe df_meanCentroid with the new centroids
def getCentroid(df_centroids,df_Xinput,list_clusterAssign):

 numCentroids=df_centroids.shape[0]
 k_counts=[] #divide colums by the number of occurances each class
 for k in range(numCentroids):
   k_counts.append(0)
 numRows=df_Xinput.shape[0]
 numCol=df_Xinput.shape[1]
 df_meanCentroid=df_centroids.copy()
 df_meanCentroid[:] = 0

 #talle column values and take k count
 for row in range(numRows):
   Xrow= list(df_Xinput.iloc[row])
   Addr= list_clusterAssign[row]
   k_counts[Addr]+=1
   for col in range(numCol):
     Sum= Xrow[col]
     df_meanCentroid.iloc[Addr,col]+=Sum
 for k in range(numCentroids):
   for col in range(numCol):
     value=df_meanCentroid.iloc[k,col] #.value added
     D=k_counts[k]
     df_meanCentroid.iloc[k,col]= (value/D)
 return df_meanCentroid

#precondiotion:
#   df_centoid has been initialized with k rows x feature
#   df_Xinput has been initialized with rows x feature
#   int_k has no purpose
#postcondition:
     #returns a list of cluster assignments where
     #index maps to df_Xinput
#   centroid in invertainly changes value
def k_means(df_Xinput, int_k,df_centroids):

  #this is a (data point x 1) vector
  list_clustAssign=[]
  list_clustAssignPrev=[]
  initialdf=df_centroids.copy()
  #Repeat until nothing is moved around
  while(True):
    list_clustAssign=assignClassification(df_centroids,df_Xinput)
    if(list_clustAssign==list_clustAssignPrev and df_centroids.equals(initialdf)):
        break
    else:
      list_clustAssignPrev=list_clustAssign.copy()
      initialdf=df_centroids.copy()
      df_centroids=getCentroid(df_centroids,df_Xinput,list_clustAssign)
  return list_clustAssign

#precondition:
#   df_data is sorted by column 4 and column 4 cotains class labels
#postcondition:
#   list_classranges has been cleared and filled with new ranges
def Gatherclasses(df_data,list_classranges,classPos):
 list_classranges.clear()
 #classes = df_data.iloc[:,4].values
 classes = df_data.iloc[:,classPos].values
 length = df_data.iloc[:,classPos].size
 list_classranges.append(0)
 flowertype=classes[0]

 for count in range(length):
  if(flowertype!=classes[count]):
    list_classranges.append(count)
    flowertype=classes[count]
 list_classranges.append(length)
 return

#precondition:
#   df_centroids: centrods
#   df: datatable with cluster assignments
#postcondition:
#   returns the SSE https://hlab.stanford.edu/brian/error_sum_of_squares.html
#   df has been sorted
def computeSSE(df_centroids,df):

 df.sort_values("class", inplace=True)
 list_classranges=[]
 Gatherclasses(df,list_classranges,4)

 Sum=0
 for everycluster in range(len(list_classranges)-1):
    df_cluster=df.iloc[list_classranges[everycluster]:list_classranges[everycluster+1],:-1]
    numRows=df_cluster.shape[0]
    for row in range(numRows):
       dist= minkowskiDist(list(df_centroids.iloc[everycluster]),list(df_cluster.iloc[row]),2)
       Sum+=dist
 return Sum
def k_meansKneePlot(df_data):
 x=[]
 y=[]
 for k in range(1,11):
   df_data = df_data.sample(frac=1).reset_index(drop=True)
   df=df_data.copy()
   X_input = df_data.iloc[:,:-1].copy()
   centroid= X_input.iloc[0:k,:].copy()
   cAssign=k_means(X_input, k,centroid)
   df.iloc[:,-1]=cAssign
   catch=computeSSE(centroid,df)
   y.append(catch)
   x.append(k)
 plt.scatter(x,y)
 plt.plot( x,y, marker='o', markerfacecolor='blue', markersize=8, color='skyblue', linewidth=1)
 plt.title('Knee Plot')
 plt.ylabel('SSE')
 plt.xlabel('Clusters')
 plt.savefig('Knee Plot')
 return
#precondition: df_Xinput is a dataTable with class labels in the last column
#postcondition: Retutns
def kmeanspp(df_Xinput, K):

 list_tuple_kdist=[]
 tuple_nearestCenters=[]

 maxCentroid=K

 numRows=df_Xinput.shape[0]
# S1:Choose one center uniformly at random from among the data points.
 df_centroids=df_Xinput.iloc[0:1:].copy()

# For each data point x, compute D(x), the distance between x and
 for centr in range(2,maxCentroid):
   for row in range(numRows):
     numCentroids=df_centroids.shape[0]
     for k in range(numCentroids):
       dist= minkowskiDist(list(df_centroids.iloc[k]),list(df_Xinput.iloc[row]),2)
       list_tuple_kdist.append([dist,row])
     # the nearest center that has already been chosen.
     list_tuple_kdist.sort(key=operator.itemgetter(0))
     tuple_nearestCenters.append(list_tuple_kdist[0])#saves {SMest dist,row} of k
     list_tuple_kdist.clear()
 # Choose one new data point as a new center,
   tuple_nearestCenters.sort(key=operator.itemgetter(0))
   tuple_centroid=tuple_nearestCenters[-1]#select largest distance tuple
   rownum=tuple_centroid[1]#select tuples row number
   df_centroids.loc[centr]=df_Xinput.iloc[rownum,:].copy()#add row in centroids
   tuple_nearestCenters.clear()
 return df_centroids
#precondition: df_Xinput is a shuffled feature matrix
def sanityCheck(data):

 data = data.sample(frac=1).reset_index(drop=True)   #shuffle the data
 df_Xinput = data.iloc[:,:-1].copy()   #feature matrix input
 Y_input= data.iloc[ :, -1:].copy() #class labels

 list_tuple_dist=[]
 numRows=df_Xinput.shape[0] # get iteration size
 df_centroids = df_Xinput.iloc[0:3,:].copy() # initialze centroids
 list_clusterAssign=k_means(df_Xinput,3,df_centroids)#get cluster ASSGNM

 for row in range(numRows):  #for every data point
   CentAddr= list_clusterAssign[row]# get centroid index for comparison
   dist= minkowskiDist(list(df_centroids.iloc[CentAddr]),list(df_Xinput.iloc[row]),2)
   list_tuple_dist.append([dist,row,CentAddr])#save the dist to sort, row for return
    #list_tuple_kdist.
 list_tuple_dist.sort(key=operator.itemgetter(2))
 df=pd.DataFrame(list_tuple_dist)
 #----------slicing the three classes df->df_c# -> list_c# ------
 list_classranges=[]
 Gatherclasses(df,list_classranges,classPos=2)

 df_c1= df.iloc[list_classranges[0]:list_classranges[1],:].copy()#slice df
 list_c1= df_c1.apply(tuple, axis=1).tolist()#create list
 list_c1.sort(key=operator.itemgetter(0))#sort
 df_c1=pd.DataFrame(list_c1) #create df


 df_c2= df.iloc[list_classranges[1]:list_classranges[2],:].copy()#slice df
 list_c2= df_c2.apply(tuple, axis=1).tolist() #create list
 list_c2.sort(key=operator.itemgetter(0)) #sort
 df_c2=pd.DataFrame(list_c2) #create df

 df_c3= df.iloc[list_classranges[2]:list_classranges[3],:]
 list_c3= df_c3.apply(tuple, axis=1).tolist()
 list_c3.sort(key=operator.itemgetter(0)) #sort
 df_c3=pd.DataFrame(list_c3) #create df
 #---------------------------------------------
 Ys=Y_input.iloc[:,0]
 #-----------------
 list_c1labels=[]
 list_c2labels=[]
 list_c3labels=[]
 for i in range(3):
  r1=df_c1.iloc[i,1]
  r2=df_c2.iloc[i,1]
  r3=df_c3.iloc[i,1]
  list_c1labels.append(Ys[r1]) #select index
  list_c2labels.append(Ys[r2]) #select index
  list_c3labels.append(Ys[r3]) #select index

 print("cluster 1 labels:",list_c1labels)
 print("\n")
 print("cluster 2 labels:",list_c2labels)
 print("\n")
 print("cluster 3 labels:",list_c3labels)
 print("\n")
 return

def k_meansErrorBarsPlot(df_data,max_iter,method):

 list_mean=[]
 list_standardDevation=[]
 list_k=[]
 for k in range(1,11):
   list_SSE=[]
   for iter in range(max_iter):#for each K run the algorithm for  max_iter
     df_data = df_data.sample(frac=1).reset_index(drop=True)#initialize
     df=df_data.copy()#initialize
     X_input = df_data.iloc[:,:-1].copy()#initialize feature matrix
     if(method=="r"):
      centroid= X_input.iloc[0:k,:].copy()#initialize k random centroids
     elif(method=="p"):
      centroid=kmeanspp(X_input, k)
     list_cAssign=k_means(X_input, k,centroid)#k_means cluster assignments
     df.iloc[:,-1]=list_cAssign #add k_means cluster assignments to df
     Value_SSE=computeSSE(centroid,df)
     list_SSE.append(Value_SSE)#record SSE

   list_mean.append(np.mean(list_SSE))# record mean
   list_standardDevation.append(np.std(list_SSE))#record standard deviation
   list_k.append(k)
 plt.figure()
 plt.errorbar(x= list_k, y=list_mean,yerr=list_standardDevation)
 if(method=="r"):
  t='k-Means Max Iteration '+str(max_iter)
 else:
  t='k-Mean++ Max Iteration '+str(max_iter)
 plt.title(t)
 plt.ylabel('SSE')
 plt.xlabel('Clusters')
 plt.savefig(t)
 plt.close()

 return
#----------- Question 1: k-Means----------
# 1)

 data=pd.read_csv('IrisDataSet.csv')  #import the data set
 data = data.sample(frac=1).reset_index(drop=True)   #shuffle the data
 X_input = data.iloc[:,:-1].copy()   #feature matrix input

 K=3
 centroid=X_input.iloc[0:K,:].copy()
 cAssign = k_means(X_input, K,centroid)

 #----------- Question 2.1: k-Means Knee Plot ----------
 data=pd.read_csv('IrisDataSet.csv')
 k_meansKneePlot(data)

  #----------- Question 2.2: Sensitivity analysis ----------

 df_data=pd.read_csv('IrisDataSet.csv')  #import the data set
 k_meansErrorBarsPlot(df_data,max_iter=2,method="r")
 k_meansErrorBarsPlot(df_data,max_iter=10,method="r")
 k_meansErrorBarsPlot(df_data,max_iter=100,method="r")

#-----------  Question 3.1: K-Means++ Initialization  ----------
 data=pd.read_csv('IrisDataSet.csv')  #import the data set
 data = data.sample(frac=1).reset_index(drop=True)   #shuffle the data
 K=4
 X_input = data.iloc[:,:-1].copy()
 centroidseed=kmeanspp(X_input, K)

#-----------  Question 3.2: K-Means++ Initialization  ----------

 k_meansErrorBarsPlot(data,max_iter=2,method="p")
 k_meansErrorBarsPlot(data,max_iter=10,method="p")
 k_meansErrorBarsPlot(data,max_iter=100,method="p")

#--------Question 4: Top data points per cluster----------------
 data=pd.read_csv('IrisDataSet.csv')  #import the data set
 sanityCheck(data)
