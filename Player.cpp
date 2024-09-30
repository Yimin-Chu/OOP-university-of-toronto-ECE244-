//
//  Player.cpp
//  Lab 2 Pong Game
//
//  Created by Author Name, Date
#include "Player.h"
#include "Screen.h"
#include <iostream>

Player::Player()
{

}

Player::Player(double x, double y, int height) {
    this->x = x;
    this->y = y;
    this->height = height;
}

double Player::getX(){return x;}

double Player::getY(){return y;} // returns the value of the y coordinate

int Player::getHeight(){return height;}// returns the height of the paddle

int Player::getWidth(){return width;} // returns the width of the paddle

void Player::decreaseHeight(int delta_to_decrease_by){
    if(height >= 3)
    {
        height = height - delta_to_decrease_by;
    }
}//decreases the height by delta_to_decrease_by amount.The minimum height is 3.

void Player::update(char c){
    if (c=='A'&& y+height+2 <= HEIGHT-1)
    {
        y = y + 2;
    }
    if(c == 'B')
    {
        if(y-2 >= 0)
            y = y - 2;
        else
            y=0;
    }
} 

void Player::draw(Screen &screen_to_draw_to) {
    for(int i=0; i < height;i++)
    {
        screen_to_draw_to.addPixel(x,y+i,'#');
    }
}
