# IMPORT LIBRARIES
from re import A
import pygame, math
from timeit import default_timer as timer


# CONSTANTEN
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)


# CLASS
class Clock():
    def __init__(self, screen, font, general_font, name, x, y, text_width, text_height, border):
        self.screen = screen

        self.font = font
        self.general_font = general_font
        self.font_number = 0

        self.name = name
        self.coordinates = (x, y)
        self.text_coordinates = (x, y-2)

        self.text_width = text_width
        self.text_height = text_height
        self.border = border

        # Zorgt ervoor dat de klokken op basis van hun naam de tekst en kleur toegewezen
        if self.name == 'clock':
            self.perspective = 'A'
            self.color = RED
        else:
            self.perspective = 'B'
            self.color = BLUE

        # ANALOG CLOCK
        self.radius = text_width/2
        self.center_pos = (self.radius+self.coordinates[0] - self.border, 620)
        self.circle_border = 10
        # Variabelen die horen bij de klok voor het station
        self.station_clock_pos = self.station_clock_pos_ref = self.station_clock_end_pos = self.station_clock_end_pos_ref = (925, 490)
        self.pointer_thickness = 3

        # TIME & DRAW
        self.start = False
        self.start_draw = False
        self.previous_time = 0.0


    def update(self):  # Update de waarde van de klok
        # Start de timer, dit kan NIET in de __init__, omdat de timer dan inaccuraat is aan het begin is van de simulatie
        if not self.start:
            self.start = True
            self.start = self.end = timer()
            self.delta_time = 0.0
            self.time = self.previous_time
        else:
            self.previous = self.end
            self.end = timer()
            self.delta_time = self.end - self.previous
            self.time += self.delta_time

        # Rekent de radialen en positie uit van de wijzer van de klok
        self.calc_radians()

        # Geeft de variable terug naar index.py, hierna wordt de variabele gepaseerd naar de klok van het andere perspectief
        return self.delta_time


    def reference_update(self, delta_time, gamma_factor):  # Update de waarde van de klok die te maken heeft met tijddillatatie
        self.gamma_factor = gamma_factor
        
        if not self.start:
            self.start = True
            self.time = self.previous_time
        else: # Verandert de tijd die bij de timer opgeteld wordt, op basis van de gammafactor(<--snelheid<--slider)
            self.time += delta_time / gamma_factor
        
        # Rekent de radialen en positie uit van de wijzer van de klok
        self.calc_radians()


    def draw(self, paused, perspective, simulation, gamma_factor):
        # GENERAL
        # Als de simulatie gepauseerd wordt, wordt de simulatie daadwerkelijk gepauseerd door deze functie te roepen
        if paused:
            self.pause_timer()

        # Zet bij de klokken de tekst A en B in het rood of in het blauw
        self.screen.blit(self.general_font[8].render(self.perspective, False, self.color), (self.coordinates[0] +99, self.coordinates[1] +232))


        # DIGITAL CLOCK - Tekent de digitale klok en verandert de grootte van de tekst in de digitale klok
        self.text = str(round(self.time, 1))
        self.text_render = self.font[self.font_number].render(self.text, False, self.color)
        
        # Elke keer dat de tijd bij een macht van 10 uitkomt: 10, 100, 1000... wordt de grootte en positie van de tekst aangepast
        if (round(self.time, 2) >= math.pow(10.00, self.font_number)):
            # De tekst renderen om te kunnen kijken wat het verschil in grootte is tussen de verschillende fonts
            # Dit kan dan weer toegepast worden op de positie van de tekst in de digitale klok
            self.text_render = self.font[self.font_number].render(self.text, False, self.color)

            self.size_before = self.font[self.font_number].size('10.00')
            self.font_number += 1
            self.size_after = self.font[self.font_number].size('10.00')

            # Compensatie voor de grootte, door de positie aan te passen, wordt hier berekend
            self.width_compensation = -1*self.font_number # (-1*self.font_number) = de verschuiving naar links van de tekst op basis van de grootte van de tekst in de digitale klok
            self.height_compensation = (self.size_before[1] - self.size_after[1])/2
            
            # De compensatie wordt hier toegepast op de coordinaten
            self.text_coordinates = (self.text_coordinates[0] + self.width_compensation, self.text_coordinates[1] + self.height_compensation)

        # Zet de positie en grootte van de klok in een variabele               
        self.rect_border = pygame.Rect(self.coordinates[0] -2*self.border, self.coordinates[1], self.text_width +2*self.border, self.text_height +self.border)
        self.rect_background = pygame.Rect(self.coordinates[0] -self.border, self.coordinates[1] +self.border, self.text_width, self.text_height -self.border)

        # Zet de klok op het scherm
        pygame.draw.rect(self.screen, WHITE, self.rect_border, 25, 10, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, BLACK, self.rect_background)

        # Zet de tekst in de klok op het scherm
        self.screen.blit(self.text_render, self.text_coordinates)


        # ANALOG CLOCK - Tekent de analoge klok
        pygame.draw.circle(self.screen, BLACK, self.center_pos, self.radius+1)
        pygame.draw.circle(self.screen, WHITE, self.center_pos, self.radius+self.circle_border+1, self.circle_border)
        pygame.draw.circle(self.screen, self.color, self.center_pos, 5)
        pygame.draw.line(self.screen, self.color, self.center_pos, self.end_pos, 3)

        if self.name == 'clock' and perspective == 'B':
            self.draw_station_clock(simulation, gamma_factor)


    def calc_radians(self):  # Rekent de radialen uit voor de functie van de klok en rekent daarna de eindpositie van de wijzer van de klok uit
        self.radians = (self.time/2)*math.pi  # Elke 4 secondes 1 rondje, want 1 rondje in 1 seconde is t*(2/1)*pi. 1 rondje in 4 secondes is t*(2/4)*pi = t*(1/2)*pi
        self.end_pos = (self.center_pos[0] + math.sin(self.radians)*self.radius, self.center_pos[1] - math.cos(self.radians)*self.radius)
    

    def draw_station_clock(self, simulation, gamma_factor):
        if simulation == 3:
            # Berekent de waardes van de klok op het gebouw, waar wel rekening is gehouden met lengtecontractie
            self.station_clock_pos_ref = (960 - (960 - self.station_clock_pos[0])/gamma_factor, self.station_clock_pos[1])
            self.station_clock_end_pos_ref = (self.station_clock_pos_ref[0] + (math.sin(self.radians)*29)/gamma_factor, self.station_clock_pos_ref[1] - math.cos(self.radians)*30)

            # Verandert de dikte van de wijzer op basis van de gamma_factor (anders blijft de wijzer erg dik op het scherm ten opzichte van de hele dunne afbeelding door lengtecontractie)
            if gamma_factor < 1.5:
                self.pointer_thickness = 3
            elif gamma_factor <= 3:
                self.pointer_thickness = 2
            else:
                self.pointer_thickness = 1

        else:
            # Berekent de waardes van de klok op het gebouw zonder rekening te houden met lengtecontractie
            self.station_clock_pos_ref = self.station_clock_pos
            self.station_clock_end_pos_ref = (self.station_clock_pos_ref[0] + (math.sin(self.radians)*29), self.station_clock_pos_ref[1] - math.cos(self.radians)*29)
            
            self.pointer_thickness = 3


        # Zet de wijzer van de klok van het gebouw op het scherm
        pygame.draw.line(self.screen, BLACK, self.station_clock_pos_ref, self.station_clock_end_pos_ref, self.pointer_thickness)


    def pause_timer(self):  # Een functie die helpt met het pauseren van de timers, door variabelen te veranderen
        self.start = False  # De klok wordt gestopt, hij is dus niet meer gestart
        self.previous_time = self.time  # Slaat de behaalde tijd van de timer bij het pauzeren op om later weer te gebruiken bij het doortellen