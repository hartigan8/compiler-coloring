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
    if(1== 1){
        if(a == 1){
            if(b == 2){
                if(c == 3){
                    return 0;
                }
                else if(c == 4){
                    return 1;
                }
                else{
                    return 2;
                }
            }
            else if(b == 4){
                return 1;
            }
            else if(b == 3){
                return 1;
            }
            else{
                return b;
            }
        }
        else if(a == 2){
            return a;
        }
        else{
            return 1;
        }
    }
    return 1;
}

