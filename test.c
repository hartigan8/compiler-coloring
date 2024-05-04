int main(){
    int a = 1;
    int b = 2 + a;
    int c = 3;
    if(a == 1){
        if(b == 2){
            if(c == 3){
                return 0;
            }
        }
    }
    return 1;
}
int test(){
    int b = 1;
    int a = 2;
    int c = a + b;
    return c;
}