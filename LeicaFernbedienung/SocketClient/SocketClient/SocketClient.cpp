// SocketClient.cpp : Defines the entry point for the console application.

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include "stdafx.h"

#define DEFAULT_PORT "8080"
#define DEFAULT_BUFLEN 5

int endExec(int code) {
	std::getchar();
	return code;
}

int main(int argc, char const *argv[])
{
	INPUT Inputs[3] = { 0 };

	Inputs[0].type = INPUT_MOUSE;
	Inputs[0].mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;

	Inputs[1].type = INPUT_MOUSE;
	Inputs[1].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;

	Inputs[2].type = INPUT_MOUSE;
	Inputs[2].mi.dwFlags = MOUSEEVENTF_LEFTUP;


	WSADATA wsaData;
	SOCKET ConnectSocket = INVALID_SOCKET;
	struct addrinfo *result = NULL,
					*ptr = NULL,
					hints;

	//char sendbuf[] = "this is a test";	//Would only be needed when sending something

	int iResult;
	char recvbuf[DEFAULT_BUFLEN];

	// Validate the parameters
	if (argc != 2) {
		printf("usage: %s server-name\n", argv[0]);
		return endExec(1);
	}

	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		printf("WSAStartup failed: %d\n", iResult);
		return endExec(1);
	}


	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	// Resolve the server address and port
	iResult = getaddrinfo(argv[1], DEFAULT_PORT, &hints, &result);
	if (iResult != 0) {
		printf("getaddrinfo failed with error: %d\n", iResult);
		WSACleanup();
		return endExec(1);
	}

	// Attempt to connect to an address until one succeeds
	for (ptr = result; ptr != NULL; ptr = ptr->ai_next) {

		// Create a SOCKET for connecting to server
		ConnectSocket = socket(ptr->ai_family, ptr->ai_socktype,
			ptr->ai_protocol);
		if (ConnectSocket == INVALID_SOCKET) {
			printf("socket failed with error: %ld\n", WSAGetLastError());
			WSACleanup();
			return endExec(1);
		}

		// Connect to server.
		iResult = connect(ConnectSocket, ptr->ai_addr, (int)ptr->ai_addrlen);
		if (iResult == SOCKET_ERROR) {
			closesocket(ConnectSocket);
			ConnectSocket = INVALID_SOCKET;
			continue;
		}
		break;
	}

	freeaddrinfo(result);

	if (ConnectSocket == INVALID_SOCKET) {
		printf("Unable to connect to server!\n");
		WSACleanup();
		return endExec(1);
	}

	/*	This is THe sending FUnction

	// Send an initial buffer
	iResult = send(ConnectSocket, sendbuf, (int)strlen(sendbuf), 0);
	if (iResult == SOCKET_ERROR) {
		printf("send failed with error: %d\n", WSAGetLastError());
		closesocket(ConnectSocket);
		WSACleanup();
		return endExec(1);
	}

	printf("Bytes Sent: %ld\n", iResult);

	// shutdown the connection since no more data will be sent
	iResult = shutdown(ConnectSocket, SD_SEND);
	if (iResult == SOCKET_ERROR) {
		printf("shutdown failed with error: %d\n", WSAGetLastError());
		closesocket(ConnectSocket);
		WSACleanup();
		return endExec(1);
	}
	*/


	// Receive until the peer closes the connection
	int x = 0;
	do {
		if (x % 5 == 0)
		{
			iResult = recv(ConnectSocket, recvbuf, sizeof(recvbuf), 0);
			



			char up = recvbuf[0];
			int u = up - '0';

			char right = recvbuf[1];
			int r = right - '0';

			char down = recvbuf[2];
			int d = down - '0';

			char left = recvbuf[3];
			int l = left - '0';

			char mid = recvbuf[4];
			int m = mid - '0';

			int y = d - u;
			int x = r - l;

			POINT mouse;
			GetCursorPos(&mouse);

			mouse.x += x*10;
			mouse.y += y*10;

			SetCursorPos(mouse.x, mouse.y);

			if (m == 1)
			{
				SendInput(3, Inputs, sizeof(INPUT));
			}

			printf("%d %d %d\n", y,x,m);

			if (iResult <= 0) {
				if (iResult == 0)
				{

					printf("Connection closed\n");
				}
				else {
					printf("recv failed with error: %d\n", WSAGetLastError());
				}
			}
		}

	} while (iResult > 0);

	// cleanup
	closesocket(ConnectSocket);
	WSACleanup();


	
	return endExec(0);
}