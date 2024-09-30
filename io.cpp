//
//  io.cpp
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

// Code taken from:
// https://stackoverflow.com/questions/61919292/c-how-do-i-erase-a-line-from-the-console
// https://stackoverflow.com/questions/11472043/non-blocking-getch
// https://stackoverflow.com/questions/421860/capture-characters-from-standard-input-without-waiting-for-enter-to-be-pressed
// https://stackoverflow.com/questions/2808398/easily-measure-elapsed-time

#include "io.h"

int green[3] = {0, 255, 0};
std::string colored_string(const std::string text, const int rgb[3]) {
  if (rgb == nullptr)
    return text;
  int r = rgb[0];
  int g = rgb[1];
  int b = rgb[2];
  std::ostringstream oss;
  oss << "\033[38;2;" << r << ";" << g << ";" << b << "m" << text << "\033[0m";
  return oss.str();
}

// checks if there are any keyboard hits. Returns the number of bytes of
// keyboard input available, or 0 if there is non
int kbhit(void) {
  static bool initflag = false;
  static const int STDIN = 0;

  if (!initflag) {
    // Use termios to turn off line buffering
    struct termios term;
    tcgetattr(STDIN, &term);
    term.c_lflag &= ~(tcflag_t)ICANON;
    tcsetattr(STDIN, TCSANOW, &term);
    setbuf(stdin, NULL);
    initflag = true;
  }

  int nbbytes;
  ioctl(STDIN, FIONREAD, &nbbytes);  // 0 is STDIN
  return nbbytes;
}

// // old code that is no longer used.
// char get_input_(){
//   if ( kbhit()>0 ) { // usually just written as `if( kbhit() )`
//     return getchar();
//   } else {
//     return '\0';
//   }
// }

std::string inputs = "";

// non blocking function that gets the keyboard press. If there are no keyboard
// presses, it returns the NULL character
char get_input() {
  if (kbhit() > 0) {  // usually just written as `if( kbhit() )`
    int input_int = getchar();
    char input = (char)input_int;
    if (input_int == EOF) {
      // Handle the EOF case, perhaps by returning a sentinel value
      input = '\0';  // or some other appropriate value
    }

    inputs += input;
    return input;
  } else {
    return '\0';
  }
}
std::string get_past_inputs() {
  std::string result = "";
  for (char c : inputs) {
    std::string modified_char = "";
    if (isprint(c)) {
      if (c == '\\') {
        modified_char += "\\\\";
      } else {
#ifdef RUNNING_WITH_PYTHON_TESTER
        modified_char += std::to_string((int)c);
#else
        modified_char += c;
#endif
      }
    } else {
      modified_char += "\\x";
      // Append the hexadecimal value
      modified_char += (c < 0x10 ? "0" : "") +
                       std::string(1, "0123456789ABCDEF"[(c >> 4) & 0x0F]);
      modified_char += std::string(1, "0123456789ABCDEF"[c & 0x0F]);
    }
#ifdef RUNNING_WITH_PYTHON_TESTER
    result += modified_char;
#else
    result += colored_string(modified_char, green) + ", ";
#endif
  }
  inputs = "";
  return result;
}

// Erases `count` lines, including the current line
void eraseLines(int count) {
  // if (count > 0) {
  //     std::cout << "\x1b[2K"; // Delete current line
  //     // i=1 because we included the first line
  //     for (int i = 1; i < count; i++) {
  //         std::cout
  //         << "\x1b[1A" // Move cursor up one
  //         << "\x1b[2K"; // Delete the entire line
  //     }
  //     std::cout << "\r"; // Resume the cursor at beginning of line
  // }
  for (int i = 0; i < count; ++i) {
#ifdef RUNNING_WITH_PYTHON_TESTER
    // no nothing, because we dont want to delete any lines when running with
    // python tester
#else
    std::cout << "\033[F";
#endif
  }
}

void clear() {
  // CSI[2J clears screen, CSI[H moves the cursor to top-left corner
  std::cout << "\x1B[2J\x1B[H";
}
