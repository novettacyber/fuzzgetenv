#include <sys/socket.h>
#include <sys/un.h>
#include <sys/types.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

#define SOCK_NAME "/tmp/fuzzsock"

char *getenv(const char *name)
{
    int sockfd;
    struct sockaddr_un addr;
    char *buf;

    if((buf = (char *)malloc(10000)) == NULL)
    {
        return NULL;
    }
    
    memset(buf, 0x00, 10000);
    
    if((sockfd = socket(AF_UNIX, SOCK_STREAM, 0)) < 0)
    {
        return NULL;
    }

    addr.sun_family = AF_UNIX;
    strcpy(addr.sun_path, SOCK_NAME);

    if(connect(sockfd, (struct sockaddr *)&addr, sizeof(struct sockaddr_un)) < 0)
    {
        return NULL;
    }

    send(sockfd, name, strlen(name), 0);
    recv(sockfd, buf, 10000, 0);

    shutdown(sockfd, SHUT_RDWR);
    close(sockfd);
    return buf;
}
