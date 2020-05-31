import os
import pygame
from pygame.locals import *

# local imports
import labels
import widgets


PRODUCTION = os.getenv("PRODUCTION")


class ReprintPanel(object):
    def __init__(self, log, screen, cultivar_data, return_handler):
        self.Log = log
        self.Screen = screen
        self.Size = self.Screen.get_size()
        self.CultivarData = cultivar_data
        self.ReturnHandler = return_handler

        self.BigFont = pygame.font.SysFont("avenir", 48)
        if self.CultivarData:
            txt = self.CultivarData.Cultivar
        else:
            txt = ""

        self.CultivarText = self.BigFont.render("Cultivar: %s"%txt, 1, widgets.BLACK)
        self.ReturnButton = widgets.ReturnButton((self.Size[0]-55, 5), self.handleReturn)

        self.TableRows = []
        self.MinusCol = 1
        self.TrayCol = 2
        self.PlusCol = 3
        self.PrevSelected = -1
        self.PrintTable = widgets.Table((50,50),
                                        (700, 400),
                                        ["        Customer        ", "       ",  "    Tray    ", "       "],
                                        self.TableRows,
                                        self.handleTableSelection)
        button_v_offset = 75
        self.OneButton = widgets.OneButton((self.Size[0]-150, 100), self.handlePrintSelection)


    def updateData(self, cultivar_data):
        self.CultivarData = cultivar_data
        self.CultivarText = self.BigFont.render("Cultivar: %s"%self.CultivarData.Cultivar, 1, widgets.BLACK)

        self.TableRows = []
        for label_set in self.CultivarData.LabelSets:
            self.TableRows.append([label_set.Customer, "-", label_set.Printed, "+"])
        
        self.PrintTable.updateRows(self.TableRows)

    def handleTableSelection(self, row, col):
        line = self.TableRows[row]
        if row != self.PrevSelected:
            # dont update unless the row is already selected
            self.PrevSelected = row
            return
        
        if col == self.MinusCol:
            line[self.TrayCol] -= 1
        elif col == self.PlusCol:
            line[self.TrayCol] += 1

        self.PrintTable.updateRows(self.TableRows, selected=row)
        return
    
    def _getLabelSetFromTable(self, idx):
        cult = self.TableRows[idx][0]
        cust = self.TableRows[idx][1]

        for label_set in self.CultivarData.LabelSets:
            if label_set.Cultivar == cult and label_set.Customer == cust:
                return label_set
        return None

    def handlePrintSelection(self):
        idx =  self.PrintTable.getSelectedRow()
        if idx < 0:
            return
        
        label_set = self._getLabelSetFromTable(idx)
        to_print = [ (label_set, self.TableRows[idx][self.TrayCol]) ]

        widgets.showPrinting(self.Screen, self.Size, self.BigFont)
        labels.printLabel(to_print)
        return

    def handleReturn(self):
        self.PrintTable.updateRows(self.TableRows)
        self.ReturnHandler()

    def handleEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self.ReturnButton.handleClick(event.pos)
            self.PrintTable.handleClick(event.pos)
            self.OneButton.handleClick(event.pos)
        return True

    def render(self):
        surface = pygame.surface.Surface(self.Size)
        pygame.draw.rect(surface, widgets.WHITE, (0,0,self.Size[0],self.Size[1]))

        surface.blit(self.CultivarText, (10, 15))
        self.ReturnButton.render(surface)
        self.PrintTable.render(surface)
        self.OneButton.render(surface)

        self.Screen.blit(surface, (0,0))
