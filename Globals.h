//
//  Globals.h
//  Lab 2 Pong Game
//
//  Created by Nathan Hung on 2024-09-11.
//  Modified by Salma Emara on 2024-09-11
//  Copyright © 2024 Nathan Hung. No rights reserved.
//
//  Permission is hereby granted to use this code in ECE244 at
//  the University of Toronto. It is prohibited to distribute
//  this code, either publicly or to third parties.
//
// ***********  ECE244 Student: DO NOT MODIFY THIS FILE  ***********

#ifndef PONG_H
#define PONG_H

#include <algorithm>
#include <cmath>
#include <string>

#define HORIZONTAL_OVERLAP -1
#define VERTICAL_OVERLAP 1
#define NO_OVERLAP 0

// Global variables
#define WIDTH 75
#define HEIGHT 39
#define simulation_fps 5000  // actually this is simulation steps per frame
#define screen_fps 60
#define milliseconds_per_frame 1000.0 / screen_fps
#define timeStep 1.0 / simulation_fps

// To ECE244 students: please ignore code below.
// #define RUNNING_WITH_PYTHON_TESTER 1 // define it if running with a python
// tester

#endif