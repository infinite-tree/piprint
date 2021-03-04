#! /usr/bin/env python3

import pygame
from pygame.locals import *
import logging
import logging.handlers
import os
import subprocess
import sys
import time


# Local imports
import reprint
import labels
import widgets

PRODUCTION = os.getenv("PRODUCTION")
SCREEN_SIZE=(800,480)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")
LOG_FILE = "~/logs/piprint_gui.log"

POWER_OFF = "sudo poweroff"


class App(object):
    def __init__(self, log):
        self.Log = log

        self.InReprint = False
        self.LabelData = []
        self.TableRows = []

        if PRODUCTION:
            # Work around for bug in libsdl
            os.environ['SDL_VIDEO_WINDOW_POS'] = "{0},{1}".format(0, 0)
            pygame.init()
            self.Screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
            pygame.mouse.set_visible(False)

            # self.Screen = pygame.display.set_mode((0, 0), FULLSCREEN)
            # pygame.mouse.set_visible(0)
        else:
            pygame.init()
            self.Screen = pygame.display.set_mode(SCREEN_SIZE)

        self.Clock = pygame.time.Clock()

        self.Size = SCREEN_SIZE
        
        # Header UI
        self.PowerButton = widgets.PowerButton((SCREEN_SIZE[0]-55, 5), self.handlePower)
        self.ReprintButton = widgets.ReprintButton((SCREEN_SIZE[0]-150, 5), self.handleReprint)
        self.BigFont = pygame.font.SysFont("avenir", 48)
        self.DateText = self.BigFont.render("Date: 00/00/0000", 1, widgets.BLACK)
        self.ReloadButton = widgets.ReloadButton((self.DateText.get_size()[0]+30, 5), self.handleReload)

        self.ReprintPanel = reprint.ReprintPanel(self.Log, self.Screen, None, self.handleReprint)

        #
        # Main UI Widgets
        #
        self.PrintTable = widgets.Table((25, 100),
                                        (700, 400),
                                        ["          Cultivar          ", "    Trays    ", "    Printed    "],
                                        self.TableRows,
                                        self.handleTableSelection)

        button_v_offset = 75
        self.OneButton = widgets.OneButton((SCREEN_SIZE[0]-150, 100), self.handlePrintOneSelection)
        self.TwoButton = widgets.TwoButton((SCREEN_SIZE[0]-150, 100+button_v_offset), self.handlePrintTwoSelection)
        self.ThreeButton = widgets.ThreeButton((SCREEN_SIZE[0]-150, 100+(button_v_offset*2)), self.handlePrintThreeSelection)
        self.FourButton = widgets.FourButton((SCREEN_SIZE[0]-150, 100+(button_v_offset*3)), self.handlePrintFourSelection)
        self.FiveButton = widgets.FiveButton((SCREEN_SIZE[0]-150, 100+(button_v_offset*4)), self.handlePrintFiveSelection)
        

    def handlePower(self):
        if PRODUCTION:
            subprocess.run(POWER_OFF, shell=True)
        else:
            sys.exit(0)

    def handleTableSelection(self, row, col):
        self.ReprintPanel.updateData(self.LabelData[row])
        return

    def handleReprint(self):
        # Toggle settings mode
        if not self.InReprint:
            self.ReprintPanel.updateData(self.LabelData[self.PrintTable.getSelectedRow()])

        self.InReprint = not self.InReprint

    def _updatePrintTable(self, selected_row=-1):
        # update listbox
        self.TableRows = []
        for cultivar_data in self.LabelData:
            self.TableRows.append([cultivar_data.Cultivar, cultivar_data.TrayCount, cultivar_data.Printed])

        self.PrintTable.updateRows(self.TableRows, selected_row)
        # if selected_row >= 0:
        #     self.ReprintPanel.updateData(self.LabelData[selected_row])

    def handleReload(self):
        self.Log.info("loading print data...")
        try:
            self.LabelData = labels.parseFile()
        except labels.LabelFileError as e:
            if "Not a CSV File" in str(e):
                self.LabelData = None
                self.Log.debug("No label data found")
            else:
                self.DateText = self.BigFont.render(str(e), 1, widgets.BLACK)
                self.Log.error("Error loading print data")
            return
        
        if self.LabelData:
            sow_date = self.LabelData[0].SowDate
            self.DateText = self.BigFont.render("Date: %s"%sow_date, 1, widgets.BLACK)
            self._updatePrintTable()
        
        self.Log.debug("Print data loaded")
        
    def _getNextLabelSet(self, cultivar):
        for label_set in cultivar.LabelSets:
            if label_set.Printed <= label_set.Trays:
                label_set.Printed += 1
                return label_set
        
        # Out of label sets, use the last one to keep adding more
        label_set = cultivar.LabelSets[-1]
        label_set.Printed += 1
        return label_set

    def handlePrintSelection(self, row_idx, quantity):
        if row_idx < 0:
            return

        to_print = []
        cultivar = self.LabelData[row_idx]
        for x in range(quantity):
            ls = self._getNextLabelSet(cultivar)
            to_print.append((ls, ls.Printed))
        
        #
        # Send info to the Printer (this can be slow)
        #
        widgets.showPrinting(self.Screen, self.Size, self.BigFont)
        labels.printLabel(to_print)

        # Wrap up
        cultivar.Printed += len(to_print)
        self._updatePrintTable(row_idx)
        labels.saveFile(self.LabelData)

    def handlePrintOneSelection(self):
        self.handlePrintSelection(self.PrintTable.getSelectedRow(), 1)

    def handlePrintTwoSelection(self):
        self.handlePrintSelection(self.PrintTable.getSelectedRow(), 2)

    def handlePrintThreeSelection(self):
        self.handlePrintSelection(self.PrintTable.getSelectedRow(), 3)

    def handlePrintFourSelection(self):
        self.handlePrintSelection(self.PrintTable.getSelectedRow(), 4)

    def handlePrintFiveSelection(self):
        self.handlePrintSelection(self.PrintTable.getSelectedRow(), 5)

    def handleEvents(self):
        now = time.time()
        for event in pygame.event.get():

            # self.Log.debug("Event: %d,%d"%event.pos)
            # self.Log.debug("Mouse: %d,%d"%pygame.mouse.get_pos())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.event.clear()
                    return False

            if event.type == QUIT:
                return False

            if self.InReprint:
                self.ReprintPanel.handleEvent(event)
            else:
                if event.type == MOUSEBUTTONDOWN:
                    self.LastMovement = now
                    # self.Log.debug("Event pos: %d,%d"%(event.pos))
                    # self.Log.debug("Start Rect: %s"%(self.StartStop.Rectangle))
                    self.PowerButton.handleClick(event.pos)
                    self.ReprintButton.handleClick(event.pos)
                    self.ReloadButton.handleClick(event.pos)
                    
                    self.PrintTable.handleClick(event.pos)
                    self.OneButton.handleClick(event.pos)
                    self.TwoButton.handleClick(event.pos)
                    self.ThreeButton.handleClick(event.pos)
                    self.FourButton.handleClick(event.pos)
                    self.FiveButton.handleClick(event.pos)

            pygame.event.clear()

        return True

    def run(self):
        while True:
            self.Clock.tick(30)
            if not self.handleEvents():
                return


            if self.InReprint:
                self.ReprintPanel.render()
            else:
                pygame.draw.rect(self.Screen, widgets.WHITE, (0,0,self.Size[0],self.Size[1]))
                self.Screen.blit(self.DateText, (10, 15))
                self.PowerButton.render(self.Screen)
                self.ReprintButton.render(self.Screen)
                self.ReloadButton.render(self.Screen)

                self.PrintTable.render(self.Screen)
                self.OneButton.render(self.Screen)
                self.TwoButton.render(self.Screen)
                self.ThreeButton.render(self.Screen)
                self.FourButton.render(self.Screen)
                self.FiveButton.render(self.Screen)

            pygame.display.flip()



if __name__ == "__main__":
    log = logging.getLogger('DryerGUILogger')
    if PRODUCTION:
        log.setLevel(logging.INFO)
    # else:
    #     log.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log_file = os.path.realpath(os.path.expanduser(LOG_FILE))
    # FIXME: TimedFileHandler
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=500000, backupCount=5)

    log.addHandler(handler)
    log.addHandler(logging.StreamHandler())
    log.info("PiPrint GUI Starting...")

    try:
        app = App(log)
        app.run()
    except Exception as e:
        log.error("Main loop failed: %s"%(e), exc_info=1)
        sys.exit(1)
