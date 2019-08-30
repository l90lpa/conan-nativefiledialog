#include <nfd.h>
#include <iostream>

int main(int argc, char** argv) {
  nfdchar_t* outPath = nullptr;

  // don't actually open a dialog because then this won't work on the
  // CI.
  std::cout << "Works!" << std::endl;

  return 0;
}
