#include "rfss.h"

Node *connection_list;
int global_server_port_num;
int server_socket_fd;

int main(int argc, char const *argv[])
{

	connection_list = NULL;
	//connection info arraylist
	fd_set readfds;
	int max_fd; // used for select, need to be update everytime when something add to fd_set
	FD_ZERO(&readfds);
	//fd_set related variables
	//int server_socket_fd;
	char flag_message_buffer[100];
	int server_flag = 0;
	int actual_rw_num = 0;
	//server part main socket
	int peer_socket_fd;
	socklen_t peerlen;
	struct sockaddr_in peer_socket_addr;
	//peer connection sockets
	int opt = 1;
	struct sockaddr_in address;
	//new implementation test variables

	//program input check 
	if (argc != 2)
	{
		printf("Usage: rfss <port number>\n");

		return 0;
	}

	global_server_port_num = atoi(argv[1]);
	// master server socket creation
	if( (server_socket_fd = socket(AF_INET , SOCK_STREAM , 0)) == 0) 
    {
        perror("socket failed");
        exit(0);
    }
  
    //set master socket to allow multiple connections , this is just a good habit, it will work without this
    if( setsockopt(server_socket_fd, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0 )
    {
        perror("setsockopt");
        exit(0);
    }
  
    //type of socket created
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( (atoi(argv[1])) );
      
    //bind the socket to localhost port 8888
    if (bind(server_socket_fd, (struct sockaddr *)&address, sizeof(address))<0) 
    {
        perror("bind failed");
        exit(0);
    }
     
    //try to specify maximum of 3 pending connections for the master socket
    if (listen(server_socket_fd, 5) < 0)
    {
        perror("listen");
        exit(0);
    }
	
    //control multiple IO reading by fd_set
	while(1)
	{

		FD_ZERO(&readfds);
		FD_SET(STDIN, &readfds);
		max_fd = STDIN;
		FD_SET(server_socket_fd, &readfds);
		max_fd = (max_fd > server_socket_fd ? max_fd : server_socket_fd);
        Node *head_ptr = connection_list;
        while(head_ptr != NULL)
        {
            if(head_ptr->recving)
                continue;

            FD_SET(head_ptr->socketfd, &readfds);
            max_fd = (max_fd > head_ptr->socketfd ? max_fd : head_ptr->socketfd);

            head_ptr = head_ptr -> next;
        }

		puts("Please enter the command: ");
		fflush(stdout);

		if(select(max_fd + 1, &readfds, NULL, NULL, NULL) < 0)
		{
			puts("select error");
			break;
		}

		if(FD_ISSET(server_socket_fd, &readfds))
		{

    		peerlen = sizeof(peer_socket_addr);
    		peer_socket_fd = accept(server_socket_fd, (struct sockaddr *) &peer_socket_addr, &peerlen);
    		if (peer_socket_fd < 0) 
          		error("ERROR on accept, error code: %d\n", peer_socket_fd);

          	//already 5 connections in the system, send full flag close it.
          	if (list_count(connection_list) >= 5)
    		{
    			server_flag = -1;
    			actual_rw_num = send(peer_socket_fd, &server_flag, sizeof(int), 0);
    			if(actual_rw_num < 0)
    				puts("server flag send error, FULL");
    			puts("Some one is trying to connect us, but the connection pool is full.");
    			close(peer_socket_fd);
    			continue;
    		}
    		else
    		{
    			//Duplication check in client, right now consider duplication connection will not be sent here
    			server_flag = 1;
    			actual_rw_num = send(peer_socket_fd, &server_flag, sizeof(int), 0);
    			if(actual_rw_num < 0)
    				puts("server flag send error, NORMAL, send flag");

    			actual_rw_num = recv(peer_socket_fd, flag_message_buffer, 100, 0);
    			if(actual_rw_num < 0)
    				puts("server flag send error, NORMAL, receive hostname");

    			printf("Accept connection request from %s\n", flag_message_buffer);

    			connection_list = list_append(connection_list, peer_socket_fd, flag_message_buffer);

    			//TODO: update FD_SET
    		}

		}

        head_ptr = connection_list;
        int receive_peer_flag = 0;
        char receive_filename[50];
        char receive_file_fullpath[100];
        strcpy(receive_file_fullpath, "Download/");
        while(head_ptr != NULL)
        {
            if(head_ptr->recving)
                continue;

            if(FD_ISSET(head_ptr->socketfd, &readfds))
            {
                actual_rw_num = recv(head_ptr->socketfd, &receive_peer_flag, sizeof(int), 0);
                if(actual_rw_num < 0)
                    puts("error when receiving peer flag integer.");
                
                if(receive_peer_flag == -1)
                {
                    //TODO: close the connnection
                    FD_CLR(head_ptr->socketfd, &readfds);
                    close(head_ptr->socketfd);

                    int delete_socket = head_ptr -> socketfd;

                    printf("The connection with %s has been terminated.\n", head_ptr->hostname);

                    head_ptr = head_ptr -> next;
                    connection_list = list_delete_with_node(connection_list, delete_socket);

                    continue;
                }
                else if(receive_peer_flag > 0)
                {
                    //prepare for receiving a file with size "receive_peer_flag"

                    actual_rw_num = recv(head_ptr->socketfd, receive_filename, 50, 0);
                    if(actual_rw_num < 0)
                        puts("error when receiving filename.");
                    bzero(receive_file_fullpath, 100);
                    strcpy(receive_file_fullpath, "Download/");
                    strcat(receive_file_fullpath, receive_filename);


                    server_flag = 1;
                    actual_rw_num = send(head_ptr->socketfd, &server_flag, sizeof(int), 0);
                    if(actual_rw_num < 0)
                        puts("error when sending back READY to receive flag.");

                    //here should create a pthread to receive BIG file content
                    pthread_t thread_recv;
                    FileInfo recv_file_info;

                    recv_file_info.socketfd = head_ptr->socketfd;
                    recv_file_info.filesize = receive_peer_flag;
                    strcpy(recv_file_info.file_fullpath, receive_file_fullpath);
                    recv_file_info.recvflag = head_ptr;

                    head_ptr->recving = 1;

                    pthread_create (&thread_recv, NULL, (void *)&receive_file_content, (void *)&recv_file_info);

                }
            }

            head_ptr = head_ptr -> next;
        }


		if(FD_ISSET(STDIN, &readfds))
		{
			user_interface(server_socket_fd);
		}

	}

	return 0;
}