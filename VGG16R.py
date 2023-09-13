# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 14:29:19 2020

@author: Administrator
"""
from __future__ import division, print_function, absolute_import
import matplotlib.pyplot as plt
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import numpy as np
from random import shuffle
import os
import itertools
import json
from sklearn.metrics import confusion_matrix
from prettytable import PrettyTable
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import numpy as np
from random import shuffle


if __name__=='__main__':
    def get_pr(pos_prob, y_true):
        pos = y_true[y_true == 1]
        threshold = np.sort(pos_prob)[::-1]
        y = y_true[pos_prob.argsort()[::-1]]
        recall = [];
        precision = []
        tp = 0;
        fp = 0
        auc = 0
        for i in range(len(threshold)):
            if y[i] == 1:
                tp += 1
                recall.append(tp / len(pos))
                precision.append(tp / (tp + fp))
                auc += (recall[i] - recall[i - 1]) * precision[i]
            else:
                fp += 1
                recall.append(tp / len(pos))
                precision.append(tp / (tp + fp))
        return precision, recall, auc


    def draw_pr(index, real_test, pred_prob):
        y_ture, y_score = create_true_score(index, real_test, pred_prob)
        recall, precision, auc = get_pr(np.array(y_score), np.array(y_ture))

        # 绘制 P-R 图
        plt.figure(figsize=(10, 6))
        plt.plot(recall, precision, label="model (AUC: {:.3f})".format(auc),
                 linewidth=2)

        plt.rcParams.update({'font.family': 'Times New Roman'})
        plt.rcParams.update({'font.weight': 'normal'})
        plt.rcParams.update({'font.size': 15})
        plt.title("Precision Recall Curve for class {}".format(index))
        plt.rcParams.update({'font.family': 'Times New Roman'})
        plt.rcParams.update({'font.weight': 'normal'})
        plt.rcParams.update({'font.size': 12})
        plt.xlabel("Recall")
        plt.rcParams.update({'font.family': 'Times New Roman'})
        plt.rcParams.update({'font.weight': 'normal'})
        plt.rcParams.update({'font.size': 12})
        plt.ylabel("Precision")
        plt.rcParams.update({'font.family': 'Times New Roman'})
        plt.rcParams.update({'font.weight': 'normal'})
        plt.rcParams.update({'font.size': 10})
        plt.legend()
        plt.show()
    def create_y_true(index, real_label):
        new_label = real_label.copy()
        for i, label in enumerate(new_label):
            if label != index:
                new_label[i] = 0
            else:
                new_label[i] = 1

        return new_label


    def create_y_scores(index, pred_prob):
        scores = []
        for i, prob in enumerate(pred_prob):
            scores.append(prob[index])

        return scores


    def create_true_score(index, real_test, pred_prob):
        y_true = create_y_true(index, real_test)
        y_scores = create_y_scores(index, pred_prob)

        return y_true, y_scores


    def get_roc(pos_prob, y_true):
        pos = y_true[y_true == 1]
        neg = y_true[y_true == 0]
        threshold = np.sort(pos_prob)[::-1]
        y = y_true[pos_prob.argsort()[::-1]]
        tpr_all = [0];
        fpr_all = [0]
        tpr = 0;
        fpr = 0
        x_step = 1 / float(len(neg))
        y_step = 1 / float(len(pos))
        y_sum = 0
        for i in range(len(threshold)):
            if y[i] == 1:
                tpr += y_step
                tpr_all.append(tpr)
                fpr_all.append(fpr)
            else:
                fpr += x_step
                fpr_all.append(fpr)
                tpr_all.append(tpr)
                y_sum += tpr
        return fpr_all, tpr_all, y_sum * x_step

    class ConfusionMatrix(object):
        """
        注意，如果显示的图像不全，是matplotlib版本问题
        本例程使用matplotlib-3.2.1(windows and ubuntu)绘制正常
        需要额外安装prettytable库
        """

        def __init__(self, num_classes: int, labels: list):
            self.matrix = np.zeros((num_classes, num_classes))
            self.num_classes = num_classes
            self.labels = labels

        def update(self, preds, labels):
            for p, t in zip(preds, labels):
                self.matrix[p, t] += 1

        def summary(self):
            # calculate accuracy
            sum_TP = 0
            for i in range(self.num_classes):
                sum_TP += self.matrix[i, i]
            acc = sum_TP / np.sum(self.matrix)
            print("the model accuracy is ", acc)

            # precision, recall, specificity
            table = PrettyTable()
            table.field_names = ["", "Precision", "Recall", "Specificity"]
            for i in range(self.num_classes):
                TP = self.matrix[i, i]
                FP = np.sum(self.matrix[i, :]) - TP
                FN = np.sum(self.matrix[:, i]) - TP
                TN = np.sum(self.matrix) - TP - FP - FN
                Precision = round(TP / (TP + FP), 3) if TP + FP != 0 else 0.
                Recall = round(TP / (TP + FN), 3) if TP + FN != 0 else 0.
                Specificity = round(TN / (TN + FP), 3) if TN + FP != 0 else 0.
                table.add_row([self.labels[i], Precision, Recall, Specificity])
            print(table)

        def plot(self):
            matrix = self.matrix
            print(matrix)
            plt.imshow(matrix, cmap=plt.cm.Blues)

            # 设置x轴坐标label
            plt.xticks(range(self.num_classes), self.labels, rotation=45)
            # 设置y轴坐标label
            plt.yticks(range(self.num_classes), self.labels)
            # 显示colorbar
            plt.colorbar()
            plt.xlabel('True Labels')
            plt.ylabel('Predicted Labels')
            plt.title('Confusion matrix')
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False
            # 在图中标注数量/概率信息
            thresh = matrix.max() / 2
            for x in range(self.num_classes):
                for y in range(self.num_classes):
                    # 注意这里的matrix[y, x]不是matrix[x, y]
                    info = int(matrix[y, x])
                    plt.text(x, y, info,
                             verticalalignment='center',
                             horizontalalignment='center',
                             color="white" if info > thresh else "black")
            plt.tight_layout()
            plt.show()

    n_class = 10
    
    #读取数据集
    train_data_file = 'DataX.npy'
    train_lable_file = 'LableY.npy'
    DataArray = np.load(train_data_file)        
    LabelArray = np.load(train_lable_file)
    
    # 对数据集进行打乱    #
    index = [i for i in range(len(LabelArray))]
    shuffle(index)
    DataArrayA = DataArray[index, :, :, :]
    LabelArrayA = LabelArray[index, :]   
    
    # 截取90%数据进行训练，10%数据进行测试
    trainlen = int(len(LabelArray) * 0.9)
    Train_X = DataArrayA[0:trainlen,:,:,:]
    Train_Y = LabelArrayA[0:trainlen,:]
    Test_X = DataArrayA[trainlen:len(LabelArray),:,:,:]
    Test_Y = LabelArrayA[trainlen:len(LabelArray),:]
    
    # 利用tflearn构建VGG模型
    tflearn.init_graph(num_cores=4, gpu_memory_fraction=0.7)#限制GPU使用内存
    # Building 'VGG Network'以下为模型的加载，其中3是卷积核的大小即3*3.64/128/256/512是卷积核的个数
    network = input_data(shape=[None, 227, 227, 3])
    
    network = conv_2d(network, 64, 3, activation='relu')
    network = conv_2d(network, 64, 3, activation='relu')
    network = max_pool_2d(network, 2, strides=2)
    
    network = conv_2d(network, 128, 3, activation='relu')
    network = conv_2d(network, 128, 3, activation='relu')
    network = max_pool_2d(network, 2, strides=2)
    
    network = conv_2d(network, 256, 3, activation='relu')
    network = conv_2d(network, 256, 3, activation='relu')
    network = conv_2d(network, 256, 3, activation='relu')
    network = max_pool_2d(network, 2, strides=2)
    
    network = conv_2d(network, 512, 3, activation='relu')
    network = conv_2d(network, 512, 3, activation='relu')
    network = conv_2d(network, 512, 3, activation='relu')
    network = max_pool_2d(network, 2, strides=2)
    
    network = conv_2d(network, 512, 3, activation='relu')
    network = conv_2d(network, 512, 3, activation='relu')
    network = conv_2d(network, 512, 3, activation='relu')
    network = max_pool_2d(network, 2, strides=2)
    
    network = fully_connected(network, 4096, activation='relu')
    network = dropout(network, 0.5)
    network = fully_connected(network, 2048, activation='relu')
    network = dropout(network, 0.5)
    network = fully_connected(network, 10, activation='softmax')
    
    network = regression(network, optimizer='momentum',
                         loss='categorical_crossentropy',
                         learning_rate=0.001)
    
    # Training
    #max_checkpoints是存储checkpoint文件的个数，如果超过个数，应该是自动删除
    model = tflearn.DNN(network, checkpoint_path='model_vgg',
                        max_checkpoints=1, tensorboard_verbose=0)
    #snapshot_step表示执行多少步后保存checkpoint文件,n_epoch是执行循环的次数，batch_size每次读取图片的个数,如果内存不足可以通过这个进行调节。
    # print(u'开始加载模型')
    #model.load('/home/ubuntu/pythonproject/tflearnproject/model_vgg-20')
    #model.load('model_vgg-30')
    model.fit(Train_X, Train_Y, n_epoch=1, shuffle=True,
              show_metric=True, batch_size=32, snapshot_step=1000,
              snapshot_epoch=False, run_id='vgg_Inception')
    
    VGG16_Res = model.predict(Test_X)
    aa=VGG16_Res.argmax(axis=1)
    ab=Test_Y.argmax(axis=1)
    acc=(np.sum(aa==ab)/len(aa))
    print('VGG16 Test acc is',acc)

    label_path = './class_indices.json'
    assert os.path.exists(label_path), "cannot find {}".format(label_path)
    json_file = open(label_path, 'r', encoding='UTF-8')
    class_indict = json.load(json_file)

    labels = [label for _, label in class_indict.items()]
    confusion = ConfusionMatrix(num_classes=10, labels=labels)
    confusion.update(aa, ab)
    confusion.plot()
    confusion.summary()
    def draw(index,real_test,pred_prob):
        y_true, y_scores = create_true_score(index,real_test,pred_prob)
        fpr,tpr,auc =get_roc(np.array(y_scores),np.array(y_true))
        lw = 2
        # auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, color='darkorange',
                 lw=lw, label='ROC curve (area = %0.5f)' % auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1])
        plt.ylim([0.0, 1])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic example')
        plt.legend(loc="lower right")
        plt.show()



    for i in range(10):
        draw(i,ab,VGG16_Res)

    for i in range(10):
        draw_pr(i, ab, VGG16_Res)