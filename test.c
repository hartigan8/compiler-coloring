int test(){

    int a = 1; // 
    int b = 2; // 
    int c = 3; // b
    a = b + c; // bc
    int d = - a; // a
    if (a > b){ // bdca // abd
        a = b + 1; // bd
    }
    else{
        a = c - 1; //bdc
    }
    int f = 5; //abd
    int e = d + f + a + b; // abdf
    return a/b; // ab
}

int main(){
    int a = 1;
    int b = 2;
    int c = 3;
    a = b + c;
    int d = - a;
    int f = 5;
    int e = d + f;
    f = 2 * e;
    b = d + e;
    e = e -1;
    b = f + c;
    return a/b;
}