# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 13:29:58 2022

@author: kl0ou
"""

import random
import numpy as np
import pickle
import os
import math
import glob
import shutil
import subprocess
import matplotlib.pyplot as plt


def calcAntPoly(x, y, ang):
    
    a = 0.5
    
    posMat = np.array([[                 0,                -a/2,                 a/2],
                       [a*np.sqrt(3)/2*2/3, -a*np.sqrt(3)/2*1/3, -a*np.sqrt(3)/2*1/3]])
    
    rotMat = np.array([[np.cos(np.deg2rad(-ang)), -np.sin(np.deg2rad(-ang))],
                       [np.sin(np.deg2rad(-ang)),  np.cos(np.deg2rad(-ang))]])
    
    posPoly = np.dot(rotMat, posMat)
    posPolyXY = posPoly + [[x+0.5], [y+0.5]]
    
    return(posPolyXY.T.tolist())


def creFigure(endStep, gridMax, folderPath):
    
    # file load
    file_ant = open("%s/antStates.txt" % folderPath, "rb")
    antState = pickle.load(file_ant)
    file_ant.close()
    
    # file_field = open("%s/fieldStacked.txt" % folderPath, "rb")
    # fieldStacked = pickle.load(file_field)
    # file_field.close()
    
    c_other = (0.6, 0.6, 0.6)
    c_list = [(0.9-0.6*ii/(len(antState)-1), 0.9-0.6*ii/(len(antState)-1), 0.9-0.6*ii/(len(antState)-1)) for ii in range(len(antState))]
    
    ylength = ((gridMax-1)*2+1)*9/16
    xlim = [-gridMax-0.5, gridMax+0.5]
    ylim = [-ylength/2-0.5, ylength/2+0.5]
    
    # plot initialization
    fig, ax = plt.subplots(figsize=(32,18))
    
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, bottom=False, left=False, right=False, top=False,
                    width=1, length=1)
    
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_aspect('equal')
    ax.grid(color=c_other)
    ax.set_facecolor(c_list[0])
    
    plt.xticks(range(math.ceil(-gridMax-0.5), math.ceil(gridMax+0.5), 1))
    plt.yticks(range(math.ceil(-ylength/2-0.5), math.ceil(ylength/2+0.5), 1))
    
    # cell fill handle
    fillCell = {}
    
    for i_x in range(gridMax*2+1+1):
        
        fillCell[i_x] = {}
        
        for i_y in range(math.ceil(ylength+1)+1):
            
            fillCell[i_x][i_y], = ax.fill(np.array([i_x, i_x+1, i_x+1, i_x])-math.ceil(gridMax)-1, 
                                          np.array([i_y, i_y, i_y+1, i_y+1])-math.ceil(ylength/2)-1,
                                          color=c_list[0], edgecolor='none')
            
    
    # ant polygon container
    antCont = {}
    
    # last frame number
    lastFrameNo = 0
    
    ## calculation loop
    for i_cycle in range(endStep):
        
        frameoutAntCount = 0
        
        for i_ant in range(len(antState)):
            
            # ant fill
            if i_cycle == 0:
                antPoly = calcAntPoly(0, 0, 0)
                antCont[i_ant], = ax.fill(antPoly[0], antPoly[1], color=c_other, alpha=0.5, edgecolor='none', zorder=endStep)
            
            # ant state [x, y, angle, color]
            ant = antState[i_ant][i_cycle]
            
            # gridX = [ant[0], ant[0]+1.0, ant[0]+1.0, ant[0]]
            # gridY = [ant[1], ant[1], ant[1]+1.0, ant[1]+1.0]
            
            # ax.fill(gridX, gridY, color=col, edgecolor='none')
            
            if ant[0] < math.ceil(gridMax+0.5) and ant[0] >= -math.ceil(gridMax+0.5) \
                and ant[1] < math.ceil(ylength/2+0.5) and ant[1] >= -math.ceil(ylength/2+0.5):
                fillCell[ant[0]+math.ceil(gridMax)+1][ant[1]+math.ceil(ylength/2)+1].set_color(c_list[int(ant[3])])
            else:
                frameoutAntCount = frameoutAntCount + 1
            
            antXY = calcAntPoly(ant[0], ant[1], ant[2])
            antCont[i_ant].set_xy(antXY)
        
        if frameoutAntCount == len(antState):
            break
        
        print("\rfigure creating ... %05d/%05d" % (i_cycle+1, endStep), end='')
        plt.savefig("%s/fig_%05d.png" % (folderPath, i_cycle))
        
    lastFrameNo = i_cycle + 1
    plt.close()
    return(lastFrameNo)


def calcAntStatus(colorNum, antNum, endStep, antRotMat, folderPath):
    
    ## field array
    fieldLen = min(endStep*2,40000)
    field = np.zeros((fieldLen, fieldLen))
    
    ## initial position and angle
    antState = []
    
    for i_ant in range(antNum):
        # [x, y, angle]
        antState.append([[int((random.random() - 0.5)*200), int((random.random() - 0.5)*200), 
                          math.floor(random.random()*4)*90, 1]])
        field[antState[i_ant][0][0] + int(fieldLen/2), antState[i_ant][0][1] + int(fieldLen/2)] = 1
        
    ## calculation loop
    for i_cycle in range(endStep):
        
        # ant loop
        for i_ant in range(antNum):
            
            # current ant status
            # [x, y, angle]
            antCurr = antState[i_ant][i_cycle]
            
            # moving vector calculation
            if antCurr[2] == 0:
                vecMove = [0, 1]
            elif antCurr[2] == 90:
                vecMove = [1, 0]
            elif antCurr[2] == 180:
                vecMove = [0, -1]
            elif antCurr[2] == 270:
                vecMove = [-1, 0]
            
            # position and angle calculation
            antNextPos = [antCurr[0] + vecMove[0], antCurr[1] + vecMove[1]]
            if max(antNextPos) >= fieldLen/2:
                return()
            colorBefore = field[antNextPos[0] + int(fieldLen/2), antNextPos[1] + int(fieldLen/2)]
            
            antNextAng = (antCurr[2] + antRotMat[int(colorBefore)]) % 360
            colorNext = (colorBefore + 1) % colorNum
            
            # update state
            antState[i_ant].append([antNextPos[0], antNextPos[1], antNextAng, colorNext])
            field[antNextPos[0] + int(fieldLen/2), antNextPos[1] + int(fieldLen/2)] = colorNext
    
    # file save
    file_ant = open("%s/antStates.txt" % folderPath, "wb")
    pickle.dump(antState, file_ant)
    file_ant.close()
    
    return()

def main():
    
    # User Setting
    colorNum = 2 + math.floor(random.random()*4)      # number of colors (more than or equal to 2)
    antNum   = 2 + math.floor(random.random()*9)      # number of ants   (more than or equal to 1)
    endStep  = 120*60*5
    
    # ant rotation list
    # length = colorNum
    antRotMat = [90*math.floor(random.random()*3) for ii in range(colorNum)]
    antRotMat[0] = 90
    
    # plot max grid
    gridMax = 100 + 50 * math.floor(random.random()*2)
    
    # create folder
    folderPath_head = "../res/LangtonAnt_color%02d_ant%02d_step%05d" % (colorNum, antNum, endStep)
    folders = glob.glob("{}*/".format(folderPath_head))
    
    if len(folders) > 0:
        fileNo = [int(ifolder[-6:-1]) for ifolder in folders]
        iiExist = max(fileNo)
    else:
        iiExist = 0
    
    folderPath = "%s_%05d" % (folderPath_head, iiExist+1)
    os.mkdir(folderPath)
    
    calcAntStatus(colorNum, antNum, endStep, antRotMat, folderPath)
    
    lastFrame = creFigure(endStep, gridMax, folderPath)
    
    try:
        cmdStr = r'ffmpeg -r {} -i {}\fig_%05d.png -vcodec libx264 -pix_fmt yuv420p -r {} {}\LangtonAnt_animation.avi'.format(120, folderPath, 120, folderPath)
        subprocess.run(cmdStr, shell=True)
        
        figList = glob.glob("%s\\*.png" % (folderPath))
        for fig in figList:
            os.remove(fig)
        
        if lastFrame < endStep:
            
            folderPath_head2 = "%s%05d" % (folderPath_head[0:len(folderPath_head)-5], lastFrame)
            
            folders = glob.glob("{}*/".format(folderPath_head2))
            
            if len(folders) > 0:
                fileNo = [int(ifolder[-6:-1]) for ifolder in folders]
                iiExist = max(fileNo)
            else:
                iiExist = 0
        
            os.rename(folderPath, "%s_%05d" % (folderPath_head2, iiExist+1))
            
    except Exception as e:
        
        print(e)
        
        shutil.rmtree(folderPath)

if __name__ == "__main__":
    
    N_create = 2
    
    cnt = 0
    while cnt < N_create:
        
        main()
        
        cnt = cnt + 1