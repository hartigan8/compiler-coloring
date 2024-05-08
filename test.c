int test(){

    int a = 1;
    int b = 2;
    int c = 3;
    a = b + c;
    int d = - a;
    if (a > b){
        a = b + 1;
    }
    else{
        a = c - 1;
    }
    int f = 5;
    int e = d + f + a + b;
    return a/b;

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