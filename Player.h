//
//  Player.h
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

#ifndef PLAYER_H
#define PLAYER_H

#include <string>
#include "Globals.h"
#include "Screen.h"

class Player {
 public:
  Player();
  Player(double x, double y, int height);
  double getX();
  double getY();
  int getHeight();
  int getWidth();
  void update(char c);
  void draw(Screen& screen_to_draw_to);
  void decreaseHeight(int delta_to_decrease_by);

 private:
  double x, y;
  int height, width;
};

#endif  // PLAYER_H
