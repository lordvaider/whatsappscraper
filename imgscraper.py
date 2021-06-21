import pyautogui as pag
import pydirectinput as pd

pag.PAUSE = 0.3

def snipundsave(snx, sny, tlx, tly, brx, bry, imgnum, strt):

    # New snip button is located at snx sny
    # snip region is (tlx, tly) -> (brx, bry)
    # saved with name snip_<imgnum>

    pag.leftClick(snx, sny)  # Click on new snip button
    pag.mouseDown(tlx, tly, 'left')  # Start dragging screenshot capture area
    pag.mouseUp(brx, bry, 'left')  # End dragging screenshot capture area
    pag.hotkey('ctrl', 's')  # Open Save As window
    pag.typewrite('snip_{}'.format(imgnum+strt))  # Name the screenshot
    pag.hotkey('enter')  # Save screenshot


pag.leftClick(1705, 13)  # select the phone screen window
for img in range(1, 200):
    pag.press('down')  # scroll down in the call logs
    pd.press('enter')  # open up a call log
    snipundsave(1346, 71, 1526, 128, 1917, 984, img, 0)
    pag.hotkey('alt', 'tab')  # switch back to phone screen from snip tool
    pag.rightClick(1731, 591)   # move back to the call logs screen
