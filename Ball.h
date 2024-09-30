//
//  Ball.h
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

#ifndef BALL_H
#define BALL_H

#include "Globals.h"
#include "Player.h"
#include "Screen.h"



class Ball {
 public:
  Ball();
  Ball(double x, double y, double velocity_x, double velocity_y, int id);
  void update();
  void draw(Screen& screen_to_draw_to);
  void bounce(Ball arr[], int ballCount, Player player);
  int getID();
  double getX();
  int overlap(Ball& b);
  int overlap(Player& p);

 private:
  double velocity_x, velocity_y;
  double x, y;
  double width, height;
  int id;
};

#endif  // BALL_H
