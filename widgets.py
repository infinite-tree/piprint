import pygame
from pygame.locals import *
import os
import time

IMG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "img")
POWER_BTN = os.path.join(IMG_DIR, "power-btn.png")
RETURN_BTN = os.path.join(IMG_DIR, "return.png")
REPRINT_BTN = os.path.join(IMG_DIR, "reprint.png")
RELOAD_BTN = os.path.join(IMG_DIR, "reload.png")
UP_BTN = os.path.join(IMG_DIR, "up.png")
DOWN_BTN = os.path.join(IMG_DIR, "down.png")
ONE_BTN = os.path.join(IMG_DIR, "one.png")
TWO_BTN = os.path.join(IMG_DIR, "two.png")
THREE_BTN = os.path.join(IMG_DIR, "three.png")
FOUR_BTN = os.path.join(IMG_DIR, "four.png")
FIVE_BTN = os.path.join(IMG_DIR, "five.png")


WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLACK = (0, 0, 0)
DARK_GREY = (128, 128, 128)


class ImageButton(object):
    ImageFile = None
    def __init__(self, position, handler):
        self.Image = pygame.image.load(self.ImageFile)
        self.Position = position
        self.Rect = self.Image.get_rect().move(position)
        self.Handler = handler

    def render(self, surface, pos=None):
        if pos:
            self.Position = pos
            self.Rect = self.Rect.move(pos)

        surface.blit(self.Image, self.Position)

    def handleClick(self, event_pos):
        # print("Rect: %s, pos: %s"%(self.Rect, event_pos))
        if self.Rect.collidepoint(event_pos):
            self.callback()
            return True
        return False

    def callback(self):
        self.Handler()


class PowerButton(ImageButton):
    ImageFile = POWER_BTN


class ReturnButton(ImageButton):
    ImageFile = RETURN_BTN


class ReprintButton(ImageButton):
    ImageFile = REPRINT_BTN


class ReloadButton(ImageButton):
    ImageFile = RELOAD_BTN


class UpButton(ImageButton):
    ImageFile = UP_BTN


class DownButton(ImageButton):
    ImageFile = DOWN_BTN

class OneButton(ImageButton):
    ImageFile = ONE_BTN

class TwoButton(ImageButton):
    ImageFile = TWO_BTN

class ThreeButton(ImageButton):
    ImageFile = THREE_BTN

class FourButton(ImageButton):
    ImageFile = FOUR_BTN

class FiveButton(ImageButton):
    ImageFile = FIVE_BTN


def showPrinting(render_surface, size, font):
        dialog_size = (size[0]-100, size[1]-100)
        surface = pygame.surface.Surface(dialog_size, pygame.SRCALPHA)
        surface.fill(BLACK)
        pygame.draw.rect(surface, WHITE, (1,1, dialog_size[0]-2, dialog_size[1]-2))
        txt = font.render("Printing...", 1, BLACK)
        surface.blit(txt, (100, dialog_size[1]/2))
        render_surface.blit(surface, (50,50))
        pygame.display.flip()


class Table(object):
    def __init__(self, position, size, header, rows, selection_handler, font_size=38):
        self.Position = position
        self.Size = size
        self.Header = header
        self.Rows = []
        self.RowObjects = []
        self.Rectangles = []
        self.Font = pygame.font.SysFont("avenir", font_size)
        self.Selected = -1
        self.SelectedColumn = -1
        self.SelectionHandler = selection_handler

        self.HeaderText = []
        self.ColumnWidths = []
        for h in header:
            txt = self.Font.render(h, 1, BLACK)
            self.HeaderText.append(txt)
            self.ColumnWidths.append(txt.get_size()[0]+10)
        
        self.RowHeight = self.HeaderText[0].get_size()[1]+6
        self.updateRows(rows)

    def updateRows(self, rows, selected=-1):
        self.Rows = rows
        self.RowObjects = []
        self.Selected = selected
        self.SelectedColumn = -1

        for x, row in enumerate(rows):
            color = WHITE
            if x == self.Selected:
                color = DARK_GREY

            single_row = []
            for y,contents in enumerate(row):
                s = pygame.surface.Surface((self.ColumnWidths[y], self.RowHeight), pygame.SRCALPHA)
                s.fill(BLACK)
                size = s.get_size()
                pygame.draw.rect(s, color, (1,1, size[0]-2, size[1]-2))
                txt = self.Font.render(str(contents), 1, BLACK)
                s.blit(txt, (3,3))
                single_row.append(s)
            
            self.RowObjects.append(single_row)

    def getSelectedRow(self):
        return self.Selected

    def handleClick(self, event_pos):
        pos = (event_pos[0]-self.Position[0],
               event_pos[1] - self.Position[1])

        for idx, row in enumerate(self.Rectangles):
            for col, rect in enumerate(row):
                if rect.collidepoint(pos):
                    self.SelectedColumn = col
                    self.updateRows(self.Rows, idx)
                    self.SelectionHandler(idx, col)
                    return True

        return False

    def render(self, surface):
        base_surface = pygame.surface.Surface(self.Size, pygame.SRCALPHA)
        pygame.draw.rect(base_surface, WHITE,
                         (0, 0, self.Size[0], self.Size[1]))
        
        y = 5
        x = 5
        for txt in self.HeaderText:
            base_surface.blit(txt, (x, y))
            x += txt.get_size()[0]

        y += self.RowHeight
        self.Rectangles = []
        for row in self.RowObjects:
            rects = []
            x = 5
            for cell_surface in row:
                r = cell_surface.get_rect()
                r = r.move((x,y))
                rects.append(r)
                base_surface.blit(cell_surface, (x, y))
                x += cell_surface.get_size()[0]
            
            self.Rectangles.append(rects)
            y += cell_surface.get_size()[1]
        
        surface.blit(base_surface, self.Position)

