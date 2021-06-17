import pyautogui as pag
import pydirectinput as pd


def snipundsave(snx, sny, tlx, tly, brx, bry, imgnum, strt):

    # New snip button is located at snx sny
    # snip region is (tlx, tly) -> (brx, bry)
    # saved with name snip_<imgnum>

    pag.leftClick(snx, sny)
    pag.PAUSE = 0.3
    pag.mouseDown(tlx, tly, 'left')
    pag.PAUSE = 0.3
    pag.mouseUp(brx, bry, 'left')
    pag.PAUSE = 0.3
    pag.hotkey('ctrl', 's')
    pag.PAUSE = 0.3
    pag.typewrite('snip_{}'.format(imgnum+strt))
    pag.PAUSE = 0.3
    pag.hotkey('enter')
    pag.PAUSE = 0.3


pag.leftClick(1705, 13)
for img in range(1, 200):
    pag.press('down')
    pag.PAUSE = 0.3
    pd.press('enter')
    pag.PAUSE = 0.3
    snipundsave(1346, 71, 1526, 128, 1917, 984, img, 735)
    pag.PAUSE = 0.3
    pag.hotkey('alt', 'tab')
    pag.rightClick(1731, 591)
