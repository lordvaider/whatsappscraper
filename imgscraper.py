import pyautogui as pag
import pydirectinput as pd

pag.PAUSE = 0.3

def snipundsave(snx, sny, tlx, tly, brx, bry, imgnum, strt):

    # New snip button is located at snx sny
    # snip region is (tlx, tly) -> (brx, bry)
    # saved with name snip_<imgnum>

    pag.leftClick(snx, sny)
    pag.mouseDown(tlx, tly, 'left')
    pag.mouseUp(brx, bry, 'left')
    pag.hotkey('ctrl', 's')
    pag.typewrite('snip_{}'.format(imgnum+strt))
    pag.hotkey('enter')


pag.leftClick(1705, 13)
for img in range(1, 200):
    pag.press('down')
    pd.press('enter')
    snipundsave(1346, 71, 1526, 128, 1917, 984, img, 735)
    pag.hotkey('alt', 'tab')
    pag.rightClick(1731, 591)
