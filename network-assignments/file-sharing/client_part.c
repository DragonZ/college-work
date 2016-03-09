#include "rfss.h"

void *receive_file_content(void *file_info)
{

	FileInfo *recv_file_info;
	recv_file_info = (FileInfo *)file_info;

	char local_file_fullpath[100];
	int local_socketfd = recv_file_info->socketfd;
	int local_file_size = recv_file_info->filesize;
	Node *local_recvflag = recv_file_info->recvflag;
	strcpy(local_file_fullpath, recv_file_info -> file_fullpath);

	struct timeval start_time;
	struct timeval end_time;

	printf("Start receiving file named: %s\n", local_file_fullpath);
	//printf("Start receiving socketfd: %d, %d\n", recv_file_info -> socketfd);


	int recv_file_fd;
	recv_file_fd = open(local_file_fullpath, O_CREAT|O_WRONLY|O_TRUNC);
	//printf("=====recv file fd: %d, local socket: %d========\n", recv_file_fd, local_socketfd);
	//FILE * recv_file_fd;
  	//recv_file_fd = fopen (local_file_fullpath, "w");
  	//fwrite (buffer , sizeof(char), sizeof(buffer), pFile);
  	//fclose (pFile);

	//if(recv_file_fd < 0)
		//puts("error when creating download file.");

	int package_size = 1024; // need to read from config.txt. TODO

	int accumulated_size_received = 0;
	int size_received = 0; 
	char receive_package_buffer[package_size];

	if(gettimeofday(&start_time, NULL) < 0)
        		puts("error when getting recv start time.");

	while(accumulated_size_received != local_file_size)
	{

		size_received = recv(local_socketfd, receive_package_buffer, package_size, 0);
        if(size_received < 0)
        {
        	puts("error when receiving filename.");
        	close(recv_file_fd);
        	//fclose(recv_file_fd);
        	return NULL;
        }
        write(recv_file_fd, receive_package_buffer, size_received);
        //fwrite (receive_package_buffer , sizeof(char), size_received, recv_file_fd);
        accumulated_size_received += size_received;
	}

	if(gettimeofday(&end_time, NULL) < 0)
        		puts("error when getting recv end time.");

	close(recv_file_fd);
    //fclose(recv_file_fd);

	long time_interval = end_time.tv_sec * 1000000 + end_time.tv_usec - start_time.tv_sec * 1000000 - start_time.tv_usec;
    long trans_rate = accumulated_size_received * 8 / time_interval;
    char localhostname[50];
    gethostname(localhostname, 50);
    Node *from_socket_node = list_search(connection_list, local_socketfd);

    if (from_socket_node == NULL)
    {
    	puts("cannot find hostname recv from.");
    }
    else
    {
    	printf("Rx (%s): %s -> %s, File Size: %d Bytes, Time Taken: %ld microseconds, Rx Rate: %ld bits/msec\n", 
        localhostname, from_socket_node->hostname, localhostname, accumulated_size_received, time_interval, trans_rate);
    }
        	
	printf("File receive complete, at %s, file size received: %d\n", local_file_fullpath, accumulated_size_received);

	local_recvflag->recving = 0;
	/*int *socket_int = (int *)socket;
	int file_size;
	ssize_t size_received;
	char buffer[BUFFER_SIZE];

	bzero(buffer,BUFFER_SIZE);

	while(1)
	{
		size_received = 0;
		size_received = recv(*socket_int, &file_size, sizeof(int), 0);
		if (size_received)
		{
			if (file_size)
			{
				ssize_t accumulated_size_received = 0;

				//read file name first 
				size_received = recv(*socket_int, buffer, BUFFER_SIZE, 0);
				while(accumulated_size_received != file_size)
				{
					size_received = recv(*socket_int, buffer, BUFFER_SIZE, 0);
					// TODO rewrite to file 
				}
			}
		}

	}
     n = read(newsockfd,buffer,255);
     if (n < 0) error("ERROR reading from socket");
     printf("Here is the message: %s\n",buffer);
     n = write(newsockfd,"I got your message",18);
     if (n < 0) error("ERROR writing to socket");
     close(newsockfd);
     close(sockfd);
     return 0;*/

}