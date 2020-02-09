import pygame
import time
import random
import math
import numpy
from pygame import gfxdraw
import matplotlib.pyplot as plt
import statistics as stats


def main():
    pygame.init()
    game_width = 800
    game_height = 600
    
    #colors
    white = (255,255,255)
    black = (0,0,0)
    red = (255,0,0)
    green = (0,255,0)
    blue = (0,0,255)
    purple = (102, 0, 102)
    
    max_vel = 2
    fps = 30
    size = 5
    mutation_rate = 0.2
    steering_weights = 0.05
    vel_steering_weights = 0.5
    perception_radius_mutation_range = 30
    initial_perception_radius = 100
    boundary_size = 10
    max_vel = 20
    initial_max_force = 0.02
    health = 100
    max_poison = 75
    nutrition = [20, -80]
    bots = []
    food = []
    poison = []
    oldest_ever = 0
    oldest_ever_dna = []
    game_display = pygame.display.set_mode((game_width, game_height))
    clock = pygame.time.Clock()
    
    blue_counts = []
    purple_counts = []
    blue_speed = []
    purple_speed = []
    
    purple_size = []
    blue_size = []
    blue_alive = True
    purple_alive = True
    
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
        def __init__(self,x,y,type,max_vel,dna=False):
            
            #static traits
            self.age = 1
            self.type = type
            
            if type == 'blue':
                #blue
                self.color = blue #(0,0,255)
                self.health = 100
                self.reproduction_rate = 0.01
                self.max_vel = 10
                self.max_age = 100
                self.size = 3
                
            else:
                #purple
                self.color = purple
                self.health = 375
                self.reproduction_rate = 0.005
                self.max_vel = 5
                self.max_age = 400
                self.size = 7
            self.position = numpy.array([x,y],dtype = 'float64')
            
            # evolving traits
            self.max_vel = self.max_vel + random.uniform(-vel_steering_weights, vel_steering_weights)
            self.velocity = numpy.array([random.uniform(-self.max_vel,self.max_vel),random.uniform(-self.max_vel,self.max_vel)],dtype = 'float64')
            self.acceleration = numpy.array([0,0],dtype='float64')
            self.max_force = 0.5
            self.size = 5
            

            
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
            #print(self.dna)
            
        def update(self):
            self.velocity += self.acceleration
            
            self.velocity = normalize(self.velocity)*self.max_vel
            
            self.position += self.velocity
            self.acceleration *= 0  
            self.health -= self.max_vel/self.size

            #self.color = lerp()
            self.health = min(health,self.health)
            
            
            if self.age % self.max_age == 0:
                self.health = 0
            else:
                self.age +=1
            
        def reproduce(self):
            if random.random() < self.reproduction_rate:
                bots.append(create_bot(self.position[0],self.position[1],self.type,self.max_vel,self.dna))
                
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
            
    for i in range(10):
        bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'blue',5)) 
        bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'purple',2)) 
    

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Count of Species')
    
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    ax2.set_title('Speed of Species')
    
    
    
    running = True
    while(running):
        game_display.fill(black)
        #if len(bots) < 5 or random.random() < 0.0001:
         #   if random.random() > 0.5:
          #      bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'blue'))
           # else:
           #     bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height),'purple'))
        if random.random()<0.4:
            food.append(numpy.array([random.uniform(boundary_size, game_width-boundary_size), random.uniform(boundary_size, game_height-boundary_size)], dtype='float64'))
        if random.random()<0.01:
            poison.append(numpy.array([random.uniform(boundary_size, game_width-boundary_size), random.uniform(boundary_size, game_height-boundary_size)], dtype='float64'))
        if len(poison)>max_poison:
            poison.pop(0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        blue_count = 0
        purple_count = 0
        blue_avg_speed = []
        purple_avg_speed = []
        
        blue_avg_size = []
        purple_avg_size = []
        
        for bot in bots[::-1]:
            bot.eat(food,0)
            bot.eat(poison,1)
            bot.boundaries()
            bot.update()
            blues,purples = bot.count_bot()
            blue_count += blues
            purple_count += purples
            
            if bot.type == 'blue':
                blue_avg_speed.append(bot.max_vel)
                blue_avg_size.append(bot.size)
            else:
                purple_avg_speed.append(bot.max_vel)
                purple_avg_size.append(bot.size)
            
            #if bot.age > oldest_ever:
             #   oldest_ever = bot.age
              #  oldest_ever_dna = bot.dna
               # print(oldest_ever,oldest_ever_dna)
                #print(bot.max_vel)
            bot.draw_bot()
            if bot.dead():
                bots.remove(bot)
            else:
                bot.reproduce()
        try:
            print('Blue Speed',stats.mean(blue_avg_speed))

        except:
            print('Blue has died out')
            blue_alive = False
        try:
            print('Purple Speed',stats.mean(purple_avg_speed))
        except:
            print('Purple has died out')
            purple_alive = False
        for i in food:
            pygame.draw.circle(game_display,(0,255,0),(int(i[0]),int(i[1])),3)
        for i in poison:
            pygame.draw.circle(game_display,(255,0,0),(int(i[0]),int(i[1])),3)
        pygame.display.update()
        clock.tick(fps)
        
        
        blue_counts.append(blue_count)
        purple_counts.append(purple_count)
        
        line1, = ax.plot(range(1,len(blue_counts)+1), blue_counts, 'blue')
        line2, = ax.plot(range(1,len(purple_counts)+1), purple_counts, 'purple')
        #line2, = ax.plot(x, blue_count, 'r-')
        line1.set_ydata(blue_counts)
        line2.set_ydata(purple_counts)
        
        line1.set_xdata(range(1,len(blue_counts)+1))
        line2.set_xdata(range(1,len(purple_counts)+1))
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        if blue_alive == True and purple_alive == True:
            blue_speed.append(stats.mean(blue_avg_speed))
            purple_speed.append(stats.mean(purple_avg_speed))
            
            blue_size.append(stats.mean(blue_avg_size))
            purple_size.append(stats.mean(purple_avg_size))
            
            blue_line1, = ax2.plot(blue_speed)
            #blue_line1, = ax2.plot(range(1,len(blue_speed)+1), blue_speed, 'blue')
            blue_line1.set_ydata(blue_speed)
            
            blue_line1.set_xdata(blue_size)
            
            
            purple_line2, = ax2.plot(purple_speed)
            #purple_line2, = ax2.plot(range(1,len(purple_speed)+1), purple_speed, 'purple')
            purple_line2.set_ydata(purple_speed)
            purple_line2.set_xdata(purple_size)
            fig2.canvas.draw()
            fig2.canvas.flush_events()
            
        
    pygame.quit()
    quit()

main()
                
                
                
                
                
                
                
                
                
                
                