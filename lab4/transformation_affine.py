#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
GMT-7034 Photogrammétrie fondamentale
Laboratoire 4 - Transformation affine
Date de remise: 2020-02-17

Étudiants: Jean-François Bourdon   NI:908159675
           Moises Benzan Valette   NI:111256969

Description:
Permet le chargement de coordonnées selon le système photo et
leur conversion dans le système image grâce à une transformation
affine compensée.
"""

import os
import math
import numpy as np

# Chemins d'accès aux fichiers de données
wdir = r"C:\Users\Jean-Francois\Downloads\labo4"
file_xy1_points = "G03_points_xy1.txt"
file_xy2_points = "G03_points_xy2.txt"
file_xy1_valid = "G03_validation_xy1.txt"
file_xy2_valid = "G03_validation_xy2.txt"

# Fonction de chargement des fichiers de coordonnées
def load_xy(filepath, header_length):
    with open(filepath, "r") as f:
        lines = f.readlines()
    
    lines_valid = [line for line in lines if line[0] != "%"]
    nb_coord = len(lines_valid)
    arr_xy = np.zeros((nb_coord, 2), dtype=np.float32)
    
    for ii in range(0, nb_coord):
        ls_number = lines_valid[ii].split("\t")
        number_float = [float(number.strip()) for number in ls_number]
        arr_xy[ii,:] = (number_float[0], number_float[1])
    
    return arr_xy

#Fonction de construction de la matrice A
def make_A(arr_xy):
    nb_coord = arr_xy.shape[0]
    arr_A = np.zeros((nb_coord*2,6), dtype=np.float32)
    ii = 0
    for line in range(0, nb_coord*2, 2):
        arr_A[line,0] = arr_xy[ii,0]
        arr_A[line,1] = arr_xy[ii,1]
        arr_A[line,2] = 1
        arr_A[line+1,3] = arr_xy[ii,0]
        arr_A[line+1,4] = arr_xy[ii,1]
        arr_A[line+1,5] = 1
        ii += 1
    
    return arr_A

# ESTIMATION DES PARAMÈTRES
# Chargement des fichiers de coordonnées
arr_xy1_points = load_xy(os.path.join(wdir, file_xy1_points))
arr_xy2_points = load_xy(os.path.join(wdir, file_xy2_points))

# Construction de la matrice A
arr_A = make_A(arr_xy1_points)

# Construction de la matrice L
nb_coord = arr_xy2_points.shape[0]
arr_L = arr_xy2_points.reshape((nb_coord*2,1))

# Produit matriciel pour trouver les 6 coefficients (a,b,c,d,e,f)
arr_At = arr_A.transpose()
arr_X = np.linalg.inv(arr_At @ arr_A) @ arr_At @ arr_L
a,b,c,d,e,f = [float(x) for x in arr_X]

# Isolation de l'angle de rotation theta
theta = math.atan(-d/a)

# Isolation du paramètre de non-orthogonalité alpha
alpha = math.atan(b/e) - theta

#Isolation des deux facteurs d'échelle
Sx = a/math.cos(theta)
Sy = -d/math.sin(theta)

# Présentation des 6 paramètres de la transformation affine
print("\n".join(["Theta: " + str(round(math.degrees(theta),4)) + "°",
                 "Alpha: " + str(round(math.degrees(alpha),4)) + "°",
                 "Tx:    " + str(round(c,2)) + " cm",
                 "Ty:    " + str(round(f,2)) + " cm",
                 "Sx:    " + str(round(math.degrees(Sx),4)) + "°",
                 "Sy:    " + str(round(math.degrees(Sy),4)) + "°",
                 "",
                 "a: " + str(round(a,2)),
                 "b: " + str(round(b,2)),
                 "c: " + str(round(c,2)),
                 "d: " + str(round(d,2)),
                 "e: " + str(round(e,2)),
                 "f: " + str(round(f,2))]))



# VALIDATION
# Chargement des fichiers de coordonnées
arr_xy1_valid = load_xy(os.path.join(wdir, file_xy1_valid))
arr_xy2_valid = load_xy(os.path.join(wdir, file_xy2_valid))

# Construction de la matrice A
arr_A = make_A(arr_xy1_valid)

# Calcul de la matrice L transformée et arroundie au centième de centimètre
arr_L = np.around(arr_A @ arr_X, 2)

# Comparaison avec les coordonnées validées transformées
nb_coord = arr_xy1_valid.shape[0]
if np.all(arr_L.reshape(nb_coord,2) == arr_xy2_valid):
    print("Transformation affine réussie!")
else:
    print("Transformation affine échouée :(")
