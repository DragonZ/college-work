#include "rfss.h"

int get_package_size()
{

    FILE *file_fd;
    int package_size;

    file_fd = fopen("config.txt", "r");

    if (file_fd == NULL) {
      puts("error when open config file.");
      return -1;
    }

    fscanf(file_fd, "%d", &package_size);

    fclose(file_fd);

    return package_size;

}

void getIPbyHostname(char *hostname, char *ip)
{

	struct addrinfo hints, *res, *p;
    int status;
    char ipstr[INET6_ADDRSTRLEN];

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC; // AF_INET or AF_INET6 to force version
    hints.ai_socktype = SOCK_STREAM;

    if ((status = getaddrinfo(hostname, NULL, &hints, &res)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));
    }

    for(p = res;p != NULL; p = p->ai_next) {
        void *addr;
        char *ipver;

        // get the pointer to the address itself,
        // different fields in IPv4 and IPv6:
        if (p->ai_family == AF_INET) { // IPv4
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)p->ai_addr;
            addr = &(ipv4->sin_addr);
            ipver = "IPv4";
        } else { // IPv6
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)p->ai_addr;
            addr = &(ipv6->sin6_addr);
            ipver = "IPv6";
        }

        // convert the IP to a string and print it:
        inet_ntop(p->ai_family, addr, ipstr, sizeof ipstr);
        strcpy(ip, ipstr);
        freeaddrinfo(res); // free the linked list

        return;
    }

}

void error(const char *msg)
{
    perror(msg);
    exit(0);
}

int get_file_size (const char * file_name)
{
    struct stat sb;
    if (stat (file_name, & sb) != 0) {
        fprintf (stderr, "'stat' failed for '%s': %s.\n",
                 file_name, strerror (errno));
        //exit (EXIT_FAILURE);
    }
    return sb.st_size;
}

void user_interface(int server_socket_fd)
{

	char parameter[100];
	char localhostname[50];

	struct timeval start_time;
	struct timeval end_time;

	int deletion_code = -1;

	bzero(parameter, 100);
	gethostname(localhostname, 50);

	scanf("%s", parameter);

	if (!strcmp(parameter, "HELP"))
	{
		puts("Available Commands:");
		puts("HELP: Display information about the available user interface options.");
		puts("EXIT: Close all connections and terminate this process.");
		puts("MYIP: Display the IP address of this machine.");
		puts("MYPORT: Display the port on which this process is listening for incoming connections.");
		puts("CONNECT <hostname> <port number>: Establish a new connection to the machine with the specified name.");
		puts("LIST: Display a numbered list of all the connections that this process is part of.");
		puts("TERMINATE <connectionID>: This will terminate the connection listed under number when LIST is used to display all connections.");
		puts("GENERATE <filename> <filesize>: This will generate a file which is located under the local path Upload/");
		puts("UPLOAD <connectionID> <uploadfilename>: This will upload the file named upload file name which is located under the local path Upload/");
		puts("CREATOR: Display your (the student’s) full name and Purdue email address.");
	}
	else if (!strcmp(parameter, "EXIT"))
	{
		int index = 1;
		while(connection_list != NULL)
		{
			Node *node_iter = connection_list;
			connection_list = connection_list->next;

			int flag_n = send(node_iter->socketfd, &deletion_code, sizeof(int), 0);
        	if(flag_n < 0)
            	puts("error when sending deletion code of exit.");

            printf("The connection with %s has been terminated.\n", node_iter->hostname);
            close(node_iter->socketfd);
            free(node_iter);
		}

		//the server master socket need to be closed
		close(server_socket_fd);
		puts("Server master socket has been terminated.");

		exit(0);
	}
	else if (!strcmp(parameter, "MYIP"))
	{
		
		char localIP[50];
		printf("local address: %s\n", localhostname);
		getIPbyHostname(localhostname, localIP);
		printf("local IP: %s\n", localIP);
	}
	else if (!strcmp(parameter, "MYPORT"))
	{
		printf("The port we are using is: %d\n", global_server_port_num);
	}
	else if (!strcmp(parameter, "CONNECT"))
	{
		char connected_hostname[50];
		int connected_port_num = 0;
		bzero(connected_hostname, 50);
		scanf("%s", connected_hostname);
		scanf("%d", &connected_port_num);

		//there are two conditions, self and any host in the connection_list cannot be connected
		if(strstr(localhostname, connected_hostname))
		{
			puts("Cannot connect to itself.");
		}
		else if(list_contains(connection_list, connected_hostname))
		{
			puts("Duplicated connection cannot be established.");
		}
		else
		{
		int sockfd, n, flag;
    	struct sockaddr_in serv_addr;
    	struct hostent *server;
		char buffer[256];
    
    	sockfd = socket(AF_INET, SOCK_STREAM, 0);
    	if (sockfd < 0) 
        	error("ERROR opening socket");
    	server = gethostbyname(connected_hostname);
    	if (server == NULL) {
        	fprintf(stderr,"ERROR, no such host\n");
        	exit(0);
    	}
    	bzero((char *) &serv_addr, sizeof(serv_addr));
    	serv_addr.sin_family = AF_INET;
    	bcopy((char *)server->h_addr, 
         	(char *)&serv_addr.sin_addr.s_addr,
         	server->h_length);
    	serv_addr.sin_port = htons(connected_port_num);
    	if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
        	error("ERROR connecting");

    	if((n = recv(sockfd, &flag, sizeof(int), 0)) < 0)
    		puts("error when receiving server flag");

    	switch(flag){

    		case 1:
    			puts("Successful connection.");
    			bzero(buffer, 256);
    			gethostname(buffer, 256);
    			n = send(sockfd, buffer, strlen(buffer)+1, 0);
    			if (n < 0) 
         			error("ERROR when sending back hostname");
         		if(strlen(connected_hostname) < 8)
         		{
         			strcat (connected_hostname,".cs.purdue.edu");
         		}
         		connection_list = list_append(connection_list, sockfd, connected_hostname);
         		break;
        	case -1:
        		puts("Server to connect is full.");
        		close(sockfd);
        		break;
        	// case -2:
        	// 	puts("Already connect to the server.");
        	// 	close(sockfd);
        	// 	break;
        	default:
        		puts("Unknown error number.");
        		close(sockfd);
    	}
    }

	}
	else if (!strcmp(parameter, "LIST"))
	{
		Node *ptr = connection_list;
		int index = 1;
		char listIP[50];
		while(ptr != NULL)
		{
			bzero(listIP, 50);
			getIPbyHostname(ptr->hostname, listIP);
			printf("%d : %s : %s\n", index, ptr->hostname, listIP);

			index ++;
			ptr = ptr->next;
		}
	}
	else if (!strcmp(parameter, "TERMINATE"))
	{
		int deleted_connection_ID = 0;

		scanf("%d", &deleted_connection_ID);

		Node *deleted_list_node = list_nth_element(connection_list, deleted_connection_ID);
		if (deleted_list_node == NULL)
		{
			puts("Connection to delete does not exist.");
		}
		else
		{
			int deleted_socket_fd = deleted_list_node->socketfd;

			int flag_n = send(deleted_socket_fd, &deletion_code, sizeof(int), 0);
        	if(flag_n < 0)
            	puts("error when sending deletion code.");

            printf("The connection with %s has been terminated.\n", deleted_list_node->hostname);
            connection_list = list_delete(connection_list, deleted_connection_ID);
            close(deleted_socket_fd);
		}
	}
	else if (!strcmp(parameter, "GENERATE"))
	{
		char new_file_fullpath[100];
		char new_filename[50];
		char command[200];
		int new_filesize = 0;

		//FILE *new_file_fd;

		scanf("%s", new_filename);
		scanf("%d", &new_filesize);

		strcpy(new_file_fullpath, "Upload/");
		strcat(new_file_fullpath, new_filename);

		sprintf(command, "dd if=/dev/zero of=%s count=%d", new_file_fullpath, new_filesize*2);
		system(command);
		/*new_file_fd = fopen(new_file_fullpath, "w");
		if(new_file_fd == NULL)
			puts("new file was not created Successfully.");

		if(ftruncate(fileno(new_file_fd), new_filesize))
			puts("Extend file error.");

		fclose(new_file_fd);*/

	}
	else if (!strcmp(parameter, "UPLOAD"))
	{
		int connection_ID = 0;
		char upload_filename[50];
		char upload_file_fullpath[100];
		int upload_filesize = 0;
		int upload_socket_fd;
		int actual_rw_num = 0;
		int package_size = get_package_size(); //TODO: read from config.txt

		scanf("%d", &connection_ID);
		scanf("%s", upload_filename);

		strcpy(upload_file_fullpath, "Upload/");
		strcat(upload_file_fullpath, upload_filename);

		int upload_file_fd = open(upload_file_fullpath, O_RDONLY);
		if(upload_file_fd < 0 || package_size < 0)
		{
			puts("Error to open the file to upload. Or did not get valid package size from config.txt.");
		}
		else
		{
		upload_filesize = get_file_size (upload_file_fullpath);

		Node *upload_socket_info = list_nth_element(connection_list, connection_ID);
		if(upload_socket_info == NULL)
			puts("error when getting upload file socket info.");
		else
		{

		upload_socket_fd = upload_socket_info->socketfd;


		actual_rw_num = send(upload_socket_fd, &upload_filesize, sizeof(int), 0);
        if(actual_rw_num < 0)
            puts("error when sending uploading file size.");


        actual_rw_num = send(upload_socket_fd, upload_filename, strlen(upload_filename)+1, 0);
        if(actual_rw_num < 0)
            puts("error when sending uploading file name.");


        int ready_flag = 0;
        actual_rw_num = recv(upload_socket_fd, &ready_flag, sizeof(int), 0);
        if(actual_rw_num < 0)
            puts("error when receiving upload ready flag.");

        if(ready_flag == 1)
        {
        	char upload_package_buffer[package_size];
        	int file_read_flag;

        	if(gettimeofday(&start_time, NULL) < 0)
        		puts("error when getting sending start time.");

        	while((file_read_flag = read(upload_file_fd, upload_package_buffer, package_size)))
        	{
        		if (file_read_flag < 0)
        		{
        			puts("upload file reading error.");
        		}
        		else
        		{
        			actual_rw_num = send(upload_socket_fd, upload_package_buffer, file_read_flag, 0);
        			if(actual_rw_num < 0)
            			puts("error when sending uploading file contents.");
        		}
        	}
        	if(gettimeofday(&end_time, NULL) < 0)
        		puts("error when getting sending end time.");

        	long time_interval = end_time.tv_sec * 1000000 + end_time.tv_usec - start_time.tv_sec * 1000000 - start_time.tv_usec;
        	long trans_rate = upload_filesize * 8 / time_interval;

        	printf("Upload operation for file : %s, is complete.\n", upload_filename);
        	printf("Tx (%s): %s -> %s, File Size: %d Bytes, Time Taken: %ld microseconds, Tx Rate: %ld bits/msec\n", 
        		localhostname, localhostname, upload_socket_info->hostname, upload_filesize, time_interval, trans_rate);
        }
        else
        {
        	puts("No ready flag, please try again.");
        }
    }
    }
		
	}
	else if (!strcmp(parameter, "CREATOR"))
	{
		puts("Author Name: Long Zhen");
		puts("Email: lzhen@purdue.edu");
	}
	else
	{
		printf("INVALID COMMAND\n");
	}

}