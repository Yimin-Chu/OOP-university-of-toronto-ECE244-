//
//  Ball.cpp
//  Lab 2 Pong Game
//
//  Created by Author Name, Date

#include "Ball.h"
#include <iostream>
#include "Globals.h"
Ball::Ball()
{

}

Ball::Ball(double x1, double y1, double velocity_x1, double velocity_y1, int id1)
{
    width = 1;
    height = 1;
  x = x1;
  y = y1;
  velocity_x = velocity_x1;
  velocity_y = velocity_y1;
  id = id1;
}// constructor to initialized the x,y,v_x,v_y,id

double Ball::getX()
{
    return x;
} 
//returns the value of the x coordinate
int Ball::getID()
{
    return id;
} 
//returns the value of the id of the ball
void Ball::update()
{
    velocity_y = velocity_y - 0.02 * timeStep;
    y = y + velocity_y* timeStep;
    x = x + velocity_x * timeStep;
} /*velocity_y due to gravity*/

int Ball::overlap(Ball &b)

{
    if(fabs(x - b.x) < 1 && fabs(y - b.y) < 1)//1可以变成
    {
        if(fabs(y+1-b.y) > fabs(x+1-b.x))
        {
            return VERTICAL_OVERLAP;//vertical overlap
        } 
        else 
        {
            return HORIZONTAL_OVERLAP;//horizontal overlap
        }
    }//no overlap,0
    return 0;
} 
/*
check whether the balls are colliding with each other
*/

int Ball::overlap(Player &p)
{
    if ((fabs(x - p.getX()) < 1) && (y < p.getY() + p.getHeight()) && (y + height > p.getY()))
    {
        return HORIZONTAL_OVERLAP; // horizontal overlap
    }else{
        return 0;}
    
    /*if (fabs(x - p.getX()) > 1 && fabs(y - p.getY()) > 1)
    {
        if (fabs(y - p.getY()) > fabs(x - p.getX()))
            return VERTICAL_OVERLAP; // vertical overlap
        else
            return HORIZONTAL_OVERLAP; // horizontal overlap
        return NO_OVERLAP;
    } // no overlap,0*/
}

void Ball::bounce(Ball arr[], int ballCount, Player player){//
    if( x >=  WIDTH -1)//ball touch right wall
        velocity_x = - velocity_x;
    if(y <= 0 || y >= HEIGHT -1) //ball touch ground
        velocity_y = - velocity_y;
    for(int j=0; j < ballCount; j++)
    {
        if(j!=id)
        {
            if (overlap(arr[j]) == HORIZONTAL_OVERLAP) // bounce off another ball，horizontal
                velocity_x = - velocity_x;
            else if (overlap(arr[j]) == VERTICAL_OVERLAP) //bounce off another ball, vertical
                velocity_y = - velocity_y;
        }
    }
    if(overlap(player) == HORIZONTAL_OVERLAP){
        velocity_x = -velocity_x;
    }
} 

void Ball::draw(Screen& screen_to_draw_to)
{
    screen_to_draw_to.addPixel(x, y,'o');
}
