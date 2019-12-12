import pygame
import time
import random
import math
import numpy
from pygame import gfxdraw
import matplotlib.pyplot as plt


def main():
    pygame.init()
    game_width = 800
    game_height = 600
    white = (255,255,255)
    black = (0,0,0)
    red = (255,0,0)
    green = (0,255,0)
    blue = (0,0,255)
    max_vel = 20
    fps = 60
    size = 5
    mutation_rate = 0.2
    steering_weights = 0.05
    initial_perception_radius = 100
    boundary_size = 10
    max_vel = 20
    initial_max_force = 0.02
    health = 100
    max_poison = 50
    nutrition = [20, -80]
    bots = []
    food = []
    poison = []
    oldest_ever = 0
    oldest_ever_dna = []
    game_display = pygame.display.set_mode((game_width, game_height))
    clock = pygame.time.Clock()
    
    blue_counts = []
    yellow_counts = []
    
    
    def lerp():
        percent_health = bot.health/health
        lerped_color = (max(min((1-percent_health)*255,255),0), max(min(percent_health*255,255),0), 0)
        return(lerped_color)
        
    def magnitude_calc(vector):
        x = 0
        for i in vector:
            x += i**2
        magnitude = x**0.5
        return(magnitude)
    
    def normalize(vector):
        magnitude = magnitude_calc(vector)
        if magnitude != 0:
            vector = vector/magnitude
        return(vector)
    
    class create_bot():
        def __init__(self,x,y,type,dna=False):
            self.type = type
            
            self.position = numpy.array([x,y],dtype = 'float64')
            self.velocity = numpy.array([random.uniform(-max_vel,max_vel),random.uniform(-max_vel,max_vel)],dtype = 'float64')
            self.acceleration = numpy.array([0,0],dtype='float64')
            
            #self.color = color
            #self.health = health
            self.max_vel = 2
            self.max_force = 0.5
            self.size = 5
            self.age = 1
            #self.reproduction_rate = reproduction_rate
            if type == 'blue':
                #blue
                self.color = blue #(0,0,255)
                self.health = 75
                self.reproduction_rate = 0.004
                
            else:
                #yellow
                self.color = (255,255,0)
                self.health = 200
                self.reproduction_rate = 0.002
                
            if dna != False:
                self.dna = []
                for i in range(len(dna)):
                    if random.random() < mutation_rate:
                        if i < 2:
                            self.dna.append(dna[i] + random.uniform(-steering_weights, steering_weights))
                        else:
                            
                            # what is this
                            self.dna.append(dna[i] + random.uniform(-perception_radius_mutation_range, perception_radius_mutation_range))

                    else:
                        self.dna.append(dna[i])
            else:
                self.dna = [random.uniform(-initial_max_force, initial_max_force), random.uniform(-initial_max_force, initial_max_force), random.uniform(0, initial_perception_radius), random.uniform(0, initial_perception_radius)]
            print(self.dna)
            
        def update(self):
            self.velocity += self.acceleration
            
            self.velocity = normalize(self.velocity)*self.max_vel
            
            self.position += self.velocity
            self.acceleration *= 0    
            # blue species
            if self.type == 'blue':
                self.health -= 0.4
            # yellow species
            else:
                self.health-= 0.2
            #self.health -= 0.2
            #self.color = lerp()
            self.health = min(health,self.health)
            
            if self.age % 1000 == 0:
                print(self.age,self.dna)
            self.age +=1
            
        def reproduce(self):
            if random.random() < self.reproduction_rate:
                bots.append(create_bot(self.position[0],self.position[1],self.type,self.dna))
                
        def dead(self):
            if self.health > 0:
                return(False)
            else:
                if self.position[0] < game_width - boundary_size and self.position[0] > boundary_size and self.position[1] < game_height - boundary_size and self.position[1] > boundary_size:
                    food.append(self.position)
                return(True)
                
        def apply_force(self,force):
            self.acceleration += force
            
        def seek(self,target):
            desired_vel = numpy.add(target,-self.position)
            desired_vel = normalize(desired_vel)*self.max_vel
            steering_force = numpy.add(desired_vel,-self.velocity)
            steering_force = normalize(steering_force)*self.max_force
            return(steering_force)
                
        def eat(self,list_of_stuff,index):
            closest = None
            closest_distance = max(game_width,game_height)
            bot_x = self.position[0]
            bot_y = self.position[1]
            
            item_number = len(list_of_stuff)-1
            
            for i in list_of_stuff[::-1]:
                item_x = i[0]
                item_y = i[1]
                
                distance = math.hypot(bot_x-item_x,bot_y-item_y)
                
                if distance < 5:
                    list_of_stuff.pop(item_number)
                    self.health += nutrition[index]
                if distance < closest_distance:
                    closest_distance = distance
                    closest = i
                    
                item_number -= 1
                
            if closest_distance < self.dna[ 2 + index]:
                seek = self.seek(closest)
                seek *= self.dna[index]
                seek = normalize(seek)*self.max_force
                self.apply_force(seek)
                
        def boundaries(self):
            desired = None
            x_pos = self.position[0]
            y_pos = self.position[1]
            
            if x_pos < boundary_size:
                desired = numpy.array([self.max_vel,self.velocity[1]])
                steer = desired-self.velocity
                steer  = normalize(steer*self.max_force)
                self.apply_force(steer)
            elif x_pos > game_width - boundary_size:
                desired = numpy.array([-self.max_vel,self.velocity[1]])
                steer = desired-self.velocity
                steer  = normalize(steer*self.max_force)
                self.apply_force(steer)
            if y_pos < boundary_size:
                desired = numpy.array([self.velocity[0],self.max_vel])
                steer = desired-self.velocity
                steer  = normalize(steer*self.max_force)
                self.apply_force(steer)
            elif y_pos > game_width - boundary_size:
                desired = numpy.array([self.velocity[0],-self.max_vel])
                steer = desired-self.velocity
                steer  = normalize(steer*self.max_force)
                self.apply_force(steer)
                
        def draw_bot(self):
            pygame.gfxdraw.aacircle(game_display, int(self.position[0]), int(self.position[1]), 10, self.color)
            pygame.gfxdraw.filled_circle(game_display, int(self.position[0]), int(self.position[1]), 10, self.color)
            pygame.draw.circle(game_display, green, (int(self.position[0]), int(self.position[1])), abs(int(self.dna[2])), abs(int(min(2, self.dna[2]))))
            pygame.draw.circle(game_display, red, (int(self.position[0]), int(self.position[1])), abs(int(self.dna[3])), abs(int(min(2, self.dna[3]))))
            pygame.draw.line(game_display, green, (int(self.position[0]), int(self.position[1])), (int(self.position[0] + (self.velocity[0]*self.dna[0]*25)), int(self.position[1] + (self.velocity[1]*self.dna[0]*25))), 3)
            pygame.draw.line(game_display, red, (int(self.position[0]), int(self.position[1])), (int(self.position[0] + (self.velocity[0]*self.dna[1]*25)), int(self.position[1] + (self.velocity[1]*self.dna[1]*25))), 2)
            
        def count_bot(self):
            if self.type == 'blue':
                return 1,0
            else:
                return 0,1
            
    for i in range(5):
        bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'blue')) 
        bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'yellow')) 
    

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Count of Species')
    
    
    
    running = True
    while(running):
        game_display.fill(black)
        if len(bots) < 5 or random.random() < 0.0001:
            if random.random() > 0.5:
                bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'blue'))
            else:
                bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'yellow'))
        if random.random()<0.1:
            food.append(numpy.array([random.uniform(boundary_size, game_width-boundary_size), random.uniform(boundary_size, game_height-boundary_size)], dtype='float64'))
        if random.random()<0.01:
            poison.append(numpy.array([random.uniform(boundary_size, game_width-boundary_size), random.uniform(boundary_size, game_height-boundary_size)], dtype='float64'))
        if len(poison)>max_poison:
            poison.pop(0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        blue_count = 0
        yellow_count = 0
        for bot in bots[::-1]:
            bot.eat(food,0)
            bot.eat(poison,1)
            bot.boundaries()
            bot.update()
            blues,yellows = bot.count_bot()
            blue_count += blues
            yellow_count += yellows
            
            if bot.age > oldest_ever:
                oldest_ever = bot.age
                oldest_ever_dna = bot.dna
                print(oldest_ever,oldest_ever_dna)
                
            bot.draw_bot()
            if bot.dead():
                bots.remove(bot)
            else:
                bot.reproduce()
                    
        for i in food:
            pygame.draw.circle(game_display,(0,255,0),(int(i[0]),int(i[1])),3)
        for i in poison:
            pygame.draw.circle(game_display,(255,0,0),(int(i[0]),int(i[1])),3)
        pygame.display.update()
        clock.tick(fps)
        
        blue_counts.append(blue_count)
        yellow_counts.append(yellow_count)
        
        line1, = ax.plot(range(1,len(blue_counts)+1), blue_counts, 'blue')
        line2, = ax.plot(range(1,len(yellow_counts)+1), yellow_counts, 'red')
        #line2, = ax.plot(x, blue_count, 'r-')
        line1.set_ydata(blue_counts)
        line2.set_ydata(yellow_counts)
        
        line1.set_xdata(range(1,len(blue_counts)+1))
        line2.set_xdata(range(1,len(yellow_counts)+1))
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        
        
        
    pygame.quit()
    quit()

main()
                
                
                
                
                
                
                
                
                
                
                