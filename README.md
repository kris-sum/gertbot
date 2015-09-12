# gertbot

Python 2.7 compatible library for the Gertbot Raspberry Pi addon board

Work in progress.

# Example Usage

    import time,sys
    import gertbot2 as gb

    board = 3
    gb.open_uart(0)

    print("Board version: %d" % gb.get_version(board))

    gb.activate_opendrain(board,1,1)
    time.sleep(1)
    gb.activate_opendrain(board,0,0)