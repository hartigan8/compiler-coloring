int test(){
    int b = 1;
    int a = 2;
    int c = a + b;
    b = c + a;
    return c;
}

int main(){
    int a = 1;
    int b = 2 + a;
    int c = 3 + a + b;
    return c;
}

