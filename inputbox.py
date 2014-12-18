# by Timothy Downs, inputbox written for my map editor

# This program needs a little cleaning up
# It ignores the shift key
# And, for reasons of my own, this program converts "-" to "_"

# A program to get user input, allowing backspace etc
# shown in a box in the middle of the screen
# Called by:
# import inputbox
# answer = inputbox.ask(screen, "Your name")
#
# Only near the center of the screen is blitted to

import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *
class Inputbox:
  def __init__(self,line_length=10,screen=pygame.display.set_mode((360,640))):
    self.value=False
    self.line_length=line_length
    #self.clock=pygame.time.Clock()
    self.key=K_b
    self.screen = screen
    self.input_height=60
    self.output_height=100
    self.messages=[]
    pygame.font.init()
    self.fontobject = pygame.font.Font(None,18)
  def get_key(self):
    while 1:
      event = pygame.event.poll()
      if event.type == KEYDOWN:
        return event.key
      else:
        pass
    """while 1:
      event = pygame.event.poll()
      if event.type == KEYDOWN:
          self.value=True
          self.key=event.key
      elif pygame.key.get_pressed()[self.key]==0:
          self.value=False
      if self.value:
        self.clock.tick(20)
        return self.key
      else:
        pass"""
  def display_box(self, message):
    "Print a message in a box in the middle of the self.self.screen"
    pygame.draw.rect(self.screen, (0,0,0),
                     (0,self.screen.get_height()-self.input_height,self.screen.get_width(),
                      self.screen.get_height()))
    if len(message) != 0:
      self.screen.blit(self.fontobject.render(message[0:self.line_length], 1, (0,230,26),(0,0,0)),
                  (0, self.screen.get_height()-self.input_height))
    if len(message) > 10:
      for i in range(self.line_length,len(message),self.line_length):
        self.screen.blit(self.fontobject.render(message[i:i+self.line_length], 1, (0,230,26),(0,0,0)),
                    (0, self.screen.get_height()-self.input_height+i*15/self.line_length ))
    pygame.display.flip()

  def ask(self, question):
    "ask(self.screen, question) -> answer"
    pygame.font.init()
    current_string = []
    self.display_box( question + ": " + "".join(current_string))
    while 1:
      inkey = self.get_key()
      if inkey == K_BACKSPACE:

        current_string = current_string[0:-1]
      elif inkey == K_RETURN:
        break
      elif inkey == K_MINUS:
        current_string.append("_")
      elif inkey <= 127:
        current_string.append(chr(inkey))
      self.display_box( question + ": " + "".join(current_string))
    return "" .join(current_string)
  def next(self,result):
    results=[result[i:i+self.line_length] for i in range(0,len(result),self.line_length)]
    self.messages=results+self.messages
    size=int(self.output_height/15)
    if len(self.messages)>size:
      self.messages=self.messages[0:size]
    pygame.draw.rect(self.screen, (0,0,0),
                     (0,self.screen.get_height()-self.input_height-self.output_height,self.screen.get_width(),
                      self.screen.get_height()-self.output_height))
    for i in range(0,len(self.messages)):
      self.screen.blit(self.fontobject.render(self.messages[i], 1, (0,230,26),(0,0,0)),
                  (0, self.screen.get_height()-self.output_height-(i-1)*15))


  def main(self):
    result=self.ask("")
    """while result != "exit":
      self.next(result)
      result=self.ask("") """
    return result.split(" ")


if __name__ == '__main__': Inputbox(50).main()
