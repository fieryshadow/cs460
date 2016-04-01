#!/usr/bin/python
###############################################################################
# Program:
#    FinalProject Chat client
#    Brother Jones, CS 460
# Author:
#    Shane Jensen
# Summary:
#    The client for a chat communication network.
###############################################################################

import socket as socklib
import select
import sys
import io
from contextlib import contextmanager
import sys, tty, termios

#EOF='\x04'
#BACKSPACE='\x7f'

#fd = sys.stdin.fileno()
#old_settings = termios.tcgetattr(fd)

def get_stdin():
   string = ''
   fd = sys.stdin.fileno()
   old_settings = termios.tcgetattr(fd)
   try:
      tty.setraw(sys.stdin.fileno())
      while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
         ch = sys.stdin.read(1)
         if not ch:
            break
         string += ch
         #print '>>> '+string
   finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
   return string

@contextmanager
def readable_stdout():
   old_stdout = sys.stdout
   class Hider:
      def __init__(self, stream):
         self.hidden = stream
         self.data = ''
      def write(self, data):
         self.hidden.write('writing: <%s>\n' % data)
         self.data = data
      def read(self):
         return self.data
      def flush(self):
         self.hidden.flush()
   stream = Hider(old_stdout)
   sys.stdout = stream
   try:
      yield stream
   finally:
      sys.stdout = old_stdout

def main():
   ''' Serve the given port (or default) the content on the server. '''
   if len(sys.argv) != 3:
      print 'usage: python %s <host name> <port>'%(sys.argv[0])
      return
   server_host = sys.argv[1]
   server_port = int(sys.argv[2])
   sock = socklib.socket(socklib.AF_INET, socklib.SOCK_STREAM)
   sock.settimeout(2)
   try:
      sock.connect((server_host, server_port))
   except socklib.error:
      print 'Can\'t connect to server or server doesn\'t exist'
      return

   me = raw_input('Enter your username: ')
   sock.send(me)
   print 'You are now chatting'
   prompt()

   read_list = [sys.stdin, sock]
   #with readable_stdout() as stdout:
   while 1:
      read_ready, write_ready, errors = select.select(read_list, [], [])
      for reader in read_ready:
         if reader is sock:
            data = reader.recv(1024)
            if not data:
               print '\nDisconnected from server'
               return
            prev = get_stdin()
            #display(data, stdout)
            display(data, None)
            #prompt(stdout, prev)
            prompt(message=prev)
         else:
            message = sys.stdin.readline()
            sock.send(message)
            #prompt(stdout)
            prompt()

def prompt(stdout=sys.stdout, message=None):
   #if message is not None:
      #message = '<you2> ' + message
   #else:
   message = '<you> '
   stdout.write(message)
   stdout.flush()

#def display(me, username, message):
   #if username == me: username = 'you'
   #print '<%s> %s\n'%(username, message)
def display(message, stdout=None):
   #prev = stdout.read().strip()[6:] if stdout else None
   #prev = stdout.read() if stdout else None
   print '\r%s %s'%(message, 20*' ')
   #return prev

if __name__ == '__main__':
   #try:
      #tty.setraw(sys.stdin.fileno())
      main()
   #finally:
      #termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
