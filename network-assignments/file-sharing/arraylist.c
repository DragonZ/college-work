#include "rfss.h"

Node *node_construct(int socketfd, char *source_name)
{

	Node *newnode = malloc(sizeof(Node));
	newnode->socketfd = socketfd;
	strcpy(newnode->hostname, source_name);
	newnode->next = NULL;
	newnode->recving = 0;

	return newnode;

}

Node *list_append(Node *head, int socketfd, char *source_name)
{

	Node *node_append = node_construct(socketfd, source_name);
	node_append->next = head;

	return node_append;

}

int list_count(Node *head)
{

	int count = 0;

	if (head == NULL)
	{
		return 0;
	}

	while(head != NULL)
	{

		count++;
		head = head->next;

	}

	return count;

}

Node *list_delete(Node *head, int num)
{

	Node *p = head; 
	if (p == NULL)
	{
		return p;
	}
	if (num == 1)
	{
		p = p->next;
		free(head);
		return p;
	}

	Node *q = p->next;
	int count = 2;
	while ((q != NULL) && (count != num))
	{

		q = q->next;
		p = p->next;
		count++;

	}
	if(q != NULL)
	{

		p->next = q->next;
		free(q);

	}

	return head;

}

Node *list_delete_with_node(Node *head, int socket_delete)
{
	Node *p = head;
	if(p == NULL)
	{
		return p;
	}
	if((p->socketfd) == socket_delete)
	{
		p = p->next;
		free(head);
		return p;
	}

	Node *q = p->next;
	while((q != NULL) && (q -> socketfd != socket_delete))
	{
		p = p->next;
		q = q->next;
	}
	if(q != NULL)
	{
		p->next = q->next;
		free(q);
	}

	return head;
}

int list_contains(Node *head, char *userInput)
{

	Node *ptr = head;
	while(ptr != NULL)
	{
		if(strstr(ptr->hostname, userInput))
		{
			return 1;
		}
		ptr = ptr -> next;
	}

	return 0;

}

// here, the index is very special, it is from 1
Node *list_nth_element(Node *head, int index)
{

	int counter = 1;
	Node *ptr = head;

	while(ptr != NULL)
	{
		if(index == counter)
			return ptr;

		counter ++;
		ptr = ptr -> next;
	}

	return NULL;

}

Node *list_search(Node *head, int socketfd)
{

	Node *ptr = head;

	while(ptr != NULL)
	{
		if (ptr->socketfd == socketfd)
		{
			return ptr;
		}

		ptr = ptr->next;
	}

	return NULL;

}