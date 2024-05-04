int test(){
    int b = 1;
    int a = 2;
    int c = a + b;
    return c;
}

int main(){
    int a = 1;
    int b = 2 + a + test();
    int c = 3 + a + b;
    if(a == 1){
        if(b == 2){
            if(c == 3){
                return 0;
            }
        }
    }
    return 1;
}

