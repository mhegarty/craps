# -*- coding: utf-8 -*-

import logging


LOG_DIR = __file__.replace('__init__.py', '')

def game_logger(game):
    logger = logging.getLogger(str(game.id))
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
            '{}{}.log'.format(LOG_DIR, str(game.id)))
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    return logger

def no_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)
    return logger
    