#include<stdio.h>
#include<fcntl.h>
#include<unistd.h> /* read */
#include<termios.h>
#include<string.h>

#include <errno.h>
#include <string.h>

#include <fcntl.h>
#include <stdlib.h> /* EXIT_FAILURE, EXIT_SUCCESS */

#include <sys/stat.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <poll.h>
#include <time.h>

#define READ_SIZE 100

typedef struct {
   int fd; /* File descriptor */  
   char fspec[15]; /* file spec */  
   unsigned long bytes; /* bytes xfered */  
   unsigned long errors; /* errors */  
}  fifo_info_t;

int open_register_fifo(int, fifo_info_t *);
int open_serial(const char *);

int main(int argc, char *argv[]){
  
   int fd, i, rtn;
   unsigned char receive[READ_SIZE + 1];

   //struct pollfd fds_in[2];
 
   fifo_info_t fifo_info[7];
  
   struct epoll_event events[2];
 
   //----
   //printf("%d : %d : %d : %d : %d : %d : %d : %d : %d: %d\n",POLLIN,POLLRDNORM,POLLRDBAND,POLLPRI,POLLOUT,POLLWRNORM,POLLWRBAND,POLLERR,POLLHUP,POLLNVAL);exit(3);
   //----

   // Epoll 
   int epoll_fd = epoll_create1(0);
   if (epoll_fd == -1)
   {
      perror ("epoll_create");
      return -1;
   }
      
   // Create fifos... usually already created  --------------
   for (i = 0; i <= 7; i++)
   {
      // Creating demux FIFOs... which are most likely exist..
      sprintf(fifo_info[i].fspec, "./fifos/mux%d", i);
      int rtn = mkfifo(fifo_info[i].fspec, 0600);
      if ( rtn == 0 )
      {
        printf("Created mkfifo %s\n",fifo_info[i].fspec);
      }

      fd = open_register_fifo( epoll_fd, &fifo_info[i] );
   }

   // Open both serial ports  --------------
   /*
  const char *serial_ports[] = {"/dev/ttyS1","/dev/ttyS4"};
  for (i = 0; i < 2; i++)
   {
      // Opening incoming serial ports
      fd = open_serial( serial_ports[i] );
      if ( fd < 0 )
      {
         perror("UART: Failed to open.\n");
         return -1;
      }

      //fd2port[fd] = serial_ports[i];

      printf("Opened Serial Port %s %d\n",serial_ports[i],fd);
   }
    */
   
   printf("Entering while\n");
   while(1)
   {
      fifo_info_t * fifo_info_ptr;
      int fd; 
      int bytes_read;

      printf("Waiting on epoll...\n"); 
      int rdy = epoll_wait(epoll_fd, events, 8, -1);
      
      if (rdy < 0)
      {
         perror("epoll error");
         printf(">>> rdy %d %d\n",rdy,sizeof(events));
         sleep(1);
         return -1;
      }         

      // Look for input 
      for (i = 0; i < rdy; i++ )
      {
          if (events[i].events & EPOLLIN)
         {
            // read the buffer
            
            fifo_info_ptr = (fifo_info_t *)events[i].data.ptr;
            fd = fifo_info_ptr->fd;

            while( bytes_read = read(fd, receive, READ_SIZE) )
            {               
               if ( bytes_read == 0    )  { printf("zero bytes\n"); break; }
               if ( ! (bytes_read > 0 ) ) { printf("errno = %d %d %d\n",errno,bytes_read,EAGAIN); break; }

               receive[bytes_read] = '\0';
               printf("-->%s<--\n",receive);
               usleep(1000);
            }   
         }
                 
         if ( (events[i].events & EPOLLERR) ||
              (events[i].events & EPOLLHUP) ||
              (!(events[i].events & EPOLLIN)))
         {
            /* 
               An error has occurred...            
            */
            fprintf (stderr, "epoll error %d on fd %d\n",events[i].events,fd);
                                
            // Consider removing this step as when you close and immediately
            // reopen a file discriptor the fd remains the same                    
            epoll_ctl(epoll_fd, EPOLL_CTL_DEL, fd, NULL);
            close(fd);
            
            int fd_new = open_register_fifo(epoll_fd, (fifo_info_t *)(events[i].data.ptr) );

            printf("opened new descriptor %d \n", fd_new);
         }
      }
   }

   return 0;
}

// -----------------------------------------------
// Open and register fifos with epoll_fd
// -----------------------------------------------
int open_register_fifo(int epoll_fd, fifo_info_t * fifo_info_ptr)
{
   int fd;
   struct epoll_event event;

   fd = open(fifo_info_ptr->fspec, O_NONBLOCK);
   if(fd<0)
   {
      perror("Cannot open port");
      return -1;
   }

   fifo_info_ptr->fd = fd;
   
   event.events = EPOLLIN;
   event.data.ptr = fifo_info_ptr; 

   if ( epoll_ctl(epoll_fd, EPOLL_CTL_ADD, fd, &event ) )
   {
      fprintf(stderr, "Failed to add file descriptor to epoll\n");
      close(epoll_fd);
      return -1;
   }

   return(fd);
}

// -----------------------------------------------
// Open serial
// -----------------------------------------------
int open_serial(const char *dev_port) 
{
   struct termios ser_options;
   memset (&ser_options, 0, sizeof ser_options);
   int flags,s; 
   
   int fd = open(dev_port, O_WRONLY | O_NOCTTY | O_NONBLOCK); 
   if ( fd < 0 )
   {
      fprintf(stderr, "%s %s\n", strerror(errno),dev_port);
      return(-1);
   }
   
   tcgetattr(fd, &ser_options);

   ser_options.c_cflag = B115200 | CS8 |  CLOCAL;
      
   //ser_options.c_iflag = IGNPAR | ICRNL ;
   //ser_options.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl
   
   ser_options.c_oflag = 0 ;
   ser_options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
   ser_options.c_lflag |= FLUSHO;
   
   ser_options.c_cc[VMIN]  = 2;
   
   //tcflush(fd, TCIFLUSH);
   tcsetattr(fd, TCSANOW, &ser_options);

   return fd; 
}
