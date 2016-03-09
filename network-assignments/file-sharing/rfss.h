#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <pthread.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <sys/time.h>

#define MAX_CONNECTION_NUM 5
#define STDIN 0
#define BUFFER_SIZE 1024

typedef struct  listnode
{
	struct  listnode *next;
	int socketfd;
	char hostname[50];
	int recving;
} Node;

typedef struct  receive_file_info
{
	int socketfd;
	char file_fullpath[100];
	int filesize;
	Node *recvflag;
} FileInfo;

extern Node *connection_list;
extern global_server_port_num;
extern int server_socket_fd;

void user_interface(int server_socket_fd);
void *receive_file_content(void *file_info);

Node *node_construct(int socketfd, char *source_name);
Node *list_append(Node *head, int socketfd, char *source_name);
int list_count(Node *head);
Node *list_delete(Node *head, int num);
int list_contains(Node *head, char *userInput);
Node *list_nth_element(Node *head, int index);
Node *list_delete_with_node(Node *head, int socket_delete);
Node *list_search(Node *head, int socketfd);