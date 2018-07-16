#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    char *var;
    char buf[256];

    if(getenv("BAR") == NULL || strcmp("MAGIC", getenv("BAR")))
    {
        printf("Failed check.\n");
        return 1;
    }

    if((var = getenv("FOO")) == NULL)
    {
        printf("FOO is undefined.\n");
    }
    else
    {
        printf("Calling vulnerable strcpy()...\n");
        strcpy(buf, var);
        printf("buf = %s\n", buf);
    }

    return 0;
}
    
