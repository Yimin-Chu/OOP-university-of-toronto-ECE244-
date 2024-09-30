//
//  Screen.cpp
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

#include "Screen.h"

Screen::Screen() {
    printed_line_counter = 0;

    // Initialize the array2d with spaces
    for (int i = 0; i < HEIGHT; ++i) {
        for (int j = 0; j < WIDTH; ++j) {
            array2d[i][j] = ' ';
        }
    }
    frameNumber=0;
}

void Screen::putLineToBuffer(const std::string& line) {
    buffer += line + '\n';
    printed_line_counter++;
}

void Screen::renderScreen() {
    putLineToBuffer(std::string(WIDTH + 2, '-'));
    for (int i = 0; i < HEIGHT; ++i) {
        buffer += "|";
        for (int j = 0; j < WIDTH; ++j) {
            buffer += array2d[i][j];
        }
        putLineToBuffer("|");
    }
    putLineToBuffer(std::string(WIDTH + 2, '-'));
}

void Screen::showFrame(){
    std::cout<<buffer;
    std::cout.flush();
    buffer = "";
}

void Screen::clear_array2d() {
    for (int i = 0; i < HEIGHT; ++i) {
        for (int j = 0; j < WIDTH; ++j) {
            array2d[i][j] = ' ';
        }
    }
}

void Screen::deleteCurrentlyShownFrame() {
    // for (int i = 0; i < printed_line_counter; ++i) {
    //     std::cout << "\033[F";
    // }
    eraseLines(printed_line_counter);
    printed_line_counter = 0;
}

void Screen::addPixel(double x, double y, char symbol) {
    int row = HEIGHT - (int) y - 1;
    int col = (int) x;
    if (row >= HEIGHT || col >= WIDTH || row<0 || col<0) {
        return;
    }
    array2d[row][col] = symbol;
}

void Screen::update(std::string message){
    deleteCurrentlyShownFrame();
    renderScreen();
    putLineToBuffer(message);
    putLineToBuffer("This is frame "+std::to_string( (frameNumber)));
    putLineToBuffer("Received input:["+get_past_inputs()+"]!              ");
    frameNumber++;
    showFrame();
    clear_array2d();
}
