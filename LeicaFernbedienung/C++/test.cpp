#include <stdio.h>
#include <wiringPi.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string>
#include <unistd.h>
#define PORT 8080

int main(void) 
{
	//GPIO Setup
	if (wiringPiSetupPhys() == -1)
		return 1;
		
	pinMode(40,INPUT);
	pullUpDnControl(40,PUD_DOWN); //UP
	pinMode(38,INPUT);
	pullUpDnControl(38,PUD_DOWN); //RIGHT
	pinMode(37,INPUT);
	pullUpDnControl(37,PUD_DOWN); //DOWN
	pinMode(36,INPUT);
	pullUpDnControl(36,PUD_DOWN); //LEFT
	pinMode(35,INPUT);
	pullUpDnControl(35,PUD_DOWN); //MAIN
	
	//Socket Setup
	
	int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char init[6] = "22222";
      
    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
      
    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                  &opt, sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( PORT );
      
    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address, 
                                 sizeof(address))<0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, 
                       (socklen_t*)&addrlen))<0)
    {
        perror("accept");
        exit(EXIT_FAILURE);
    }
    
    
    send(new_socket , init , 5 , 0 );
    printf("Init was sent: %s\n", init);
    
    int x = 0;
	//Active Code
	while(true)
	{
		char out[] = {'0','0','0','0','0'};
	
		if (digitalRead(40) == 1)
		{
			out[0] = '1';
		}
		if (digitalRead(38) == 1)
		{
			out[1] = '1';
		}
		if (digitalRead(37) == 1)
		{
			out[2] = '1';
		}
		if (digitalRead(36) == 1)
		{
			out[3] = '1';
		}
		if (digitalRead(35) == 1)
		{
			out[4] = '1';
		}
		
		if (x % 50000 == 0)
		{
			send(new_socket , out , 5, 0 );
		}
		x++;
	}
}


