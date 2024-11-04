#include <iostream>

int Function1() {
    int num1, num2;
    std::cin >> num1 >> num2;
    return (num1 > num2) ? num1 : num2;
}