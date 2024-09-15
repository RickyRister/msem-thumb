#!/usr/bin/env python3

from argparse import ArgumentParser
import json
import math
import os.path
from urllib import request
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps
from cardimgdl import get_img_url_msem

# ============
# Constants
# ============
# Image dimensions
WIDTH = 1920
HEIGHT = 1080
DIMENSIONS = (WIDTH, HEIGHT)

# hardcoded logo dimensions
LOGO_SIZE = 352
LOGO_XY = (math.floor((WIDTH/2) - (LOGO_SIZE/2)), 233)

# hardcoded pfp position
PFP_SIZE = 303
LEFT_PFP_XY = (508, 825)
RIGHT_PFP_XY = (1073, 825)

# hardcoded card image positions
CARD_IMG_DIM = (579, 826)

LEFT_FRONT_ROT = 351.8
LEFT_BACK_ROT = 332.4
RIGHT_FRONT_ROT = 11.4
RIGHT_BACK_ROT = 23.3

LEFT_FRONT_XY = (-189, 294)
LEFT_BACK_XY = (-98, 294)
RIGHT_FRONT_XY = (1383, 332)
RIGHT_BACK_XY = (1130, 332)

# hardcoded font
TITLE_FONT = 'HelveticaNeue.ttc'
DECKNAME_FONT = 'Impact.ttf'

REGULAR = 0
BOLD = 1
BOLD_ITALICS = 3

# hardcoded text positions
# these will be horizontally centered
TITLE_POS = (WIDTH/2, -7)
SUBTITLE_POS = (WIDTH/2, 137)
LEFT_PLAYERNAME_POS = (1/5 * WIDTH, 183)
RIGHT_PLAYERNAME_POS = (4/5 * WIDTH, 183)
LEFT_DECKNAME_POS = (WIDTH/2, 667)
VS_POS = (WIDTH/2, 800)
RIGHT_DECKNAME_POS = (WIDTH/2, 906)

# Property names in config json
CARDS_XML_PATH = 'cardsXmlPath'
TITLE = 'title'
SUBTITLE = 'subtitle'
LOGO_PATH = 'logoPath'
LEFT = 'left'
RIGHT = 'right'
PLAYER_NAME = 'playerName'
DECK_NAME = 'deckName'
FRONT_CARD = 'frontCard'
BACK_CARD = 'backCard'
PFP_PATH = 'pfpPath'


def read_configs(json_path: str) -> dict:
    '''Reads in the config json
    '''
    with open(json_path) as json_file:
        return json.load(json_file)


def create_thumbnail(configs: dict) -> Image:
    '''Creates the entire thumbnail

    Returns:
        The thumbnail as an Image
    '''
    base_image = Image.new('RGB', DIMENSIONS)

    # load nested dicts to prevent nulls when traversing
    left_configs: dict = configs.get(LEFT)
    if left_configs is None:
        left_configs = dict()
    right_configs: dict = configs.get(RIGHT)
    if right_configs is None:
        right_configs = dict()

    # =====================
    # Lowest layer images
    # =====================

    # logo
    if (path := configs.get(LOGO_PATH)) is not None:
        image = Image.open(path)
        image = ImageOps.contain(image, (LOGO_SIZE, LOGO_SIZE))
        base_image.paste(image, LOGO_XY, mask=image)

    # pfp
    # left pfp
    if (path := left_configs.get(PFP_PATH)) is not None:
        image = Image.open(path)
        image = ImageOps.contain(image, (PFP_SIZE, PFP_SIZE))
        base_image.paste(image, LEFT_PFP_XY, mask=image)

    # right pfp
    if (path := right_configs.get(PFP_PATH)) is not None:
        image = Image.open(path)
        image = ImageOps.contain(image, (PFP_SIZE, PFP_SIZE))
        base_image.paste(image, RIGHT_PFP_XY, mask=image)

    # =============
    # card images
    # =============

    # load cards.xml
    cards_xml: Element = load_cards_xml(configs.get(CARDS_XML_PATH))

    # left back card
    if (cardname := left_configs.get(BACK_CARD)) is not None:
        card_image = draw_card(cardname, cards_xml, LEFT_BACK_ROT, LEFT_BACK_XY)
        base_image.paste(card_image, mask=card_image)

    # right back card
    if (cardname := right_configs.get(BACK_CARD)) is not None:
        card_image = draw_card(cardname, cards_xml, RIGHT_BACK_ROT, RIGHT_BACK_XY)
        base_image.paste(card_image, mask=card_image)

    # left front card
    if (cardname := left_configs.get(FRONT_CARD)) is not None:
        card_image = draw_card(cardname, cards_xml, LEFT_FRONT_ROT, LEFT_FRONT_XY)
        base_image.paste(card_image, mask=card_image)

    # right front card
    if (cardname := right_configs.get(FRONT_CARD)) is not None:
        card_image = draw_card(cardname, cards_xml, RIGHT_FRONT_ROT, RIGHT_FRONT_XY)
        base_image.paste(card_image, mask=card_image)

    # ======
    # Text
    # ======

    # title text
    if (text := configs.get(TITLE)) is not None:
        text_img = draw_text(text, TITLE_POS, TITLE_FONT, 130, BOLD)
        base_image.paste(text_img, mask=text_img)

    # subtitle text
    if (text := configs.get(SUBTITLE)) is not None:
        text_img = draw_text(text, SUBTITLE_POS, TITLE_FONT, 70, BOLD_ITALICS)
        base_image.paste(text_img, mask=text_img)

    # player names
    if (text := left_configs.get(PLAYER_NAME)) is not None:
        text_img = draw_text(text, LEFT_PLAYERNAME_POS, TITLE_FONT, 68, BOLD)
        base_image.paste(text_img, mask=text_img)

    if (text := right_configs.get(PLAYER_NAME)) is not None:
        text_img = draw_text(text, RIGHT_PLAYERNAME_POS, TITLE_FONT, 68, BOLD)
        base_image.paste(text_img, mask=text_img)

    # vs marker
    if True:
        text_img = draw_text('vs', VS_POS, DECKNAME_FONT, 80, REGULAR, stroke_width=2)
        base_image.paste(text_img, mask=text_img)

    # deck names
    if (text := left_configs.get(DECK_NAME)) is not None:
        text_img = draw_text(text, LEFT_DECKNAME_POS, DECKNAME_FONT, 110, REGULAR, stroke_width=2)
        base_image.paste(text_img, mask=text_img)

    if (text := right_configs.get(DECK_NAME)) is not None:
        text_img = draw_text(text, RIGHT_DECKNAME_POS, DECKNAME_FONT, 110, REGULAR, stroke_width=2)
        base_image.paste(text_img, mask=text_img)

    return base_image


def draw_text(text: str, xy: tuple[int, int], font: str, font_size: float,
              index: int = 0, stroke_width: int = 0) -> Image:
    '''Draws white text with black outlines centered at the given coords

    Args:
        text: the text to draw
        xy: coords of the textbox. Anchor is horizontal middle and verticle ascendar
        font: the font, as the name of a font file
        font_size: font size
        index: used to determine stuff like bold, italics, etc
        stroke_width: 

    Returns:
        A transparent image with the primary aspect ratio, containing just the text.
    '''
    # make a blank image for the text, initialized to transparent text color
    base_image = Image.new("RGBA", DIMENSIONS, (255, 255, 255, 0))

    # get a font
    imagefont = ImageFont.truetype(font, font_size, index)
    # get a drawing context
    d = ImageDraw.Draw(base_image)

    # draw text
    d.text(
        xy,
        text,
        align='center',
        anchor='ma',    # anchor is horizontal=mid, verticle=ascender
        font=imagefont,
        fill='white',
        stroke_width=stroke_width,
        stroke_fill='black')

    return base_image


def load_cards_xml(cards_xml_path: str) -> Element:
    '''Reads the cards.xml.
    Does null checking and expands the users in the path
    '''
    if cards_xml_path is None:
        raise ValueError('Path to cards.xml not given')
    cards_xml_path = os.path.expanduser(cards_xml_path)
    with open(cards_xml_path) as xml_file:
        etree = ElementTree.parse(xml_file)
        return etree.getroot()


def draw_card(cardname: str, cards_xml: Element,
              rotation: float, xy: tuple[int, int]) -> Image:
    '''Finds, downloads, and positions the card image

    Args:
        cardname: The card name, as it appears in cards.xml (aka on Cockatrice)
        cards_xml: cards.xml, preferrably as an Element
        rotation: card image's rotation
        xy: Coords of the top-left corner after rotation

    Returns:
        A transparent image with the primary aspect ratio, containing just the positioned image.
    '''
    # make blank base image
    base_image = Image.new("RGBA", DIMENSIONS, (255, 255, 255, 0))

    # download and position card image
    url = get_img_url_msem(cardname, cards_xml)
    card_image = Image.open(request.urlopen(url))
    card_image = ImageOps.contain(card_image, CARD_IMG_DIM)
    card_image = card_image.convert('RGBA')
    card_image = card_image.rotate(rotation, expand=True, resample=Image.BICUBIC)

    # paste image onto blank base image
    base_image.paste(card_image, xy)
    return base_image


if __name__ == "__main__":
    parser = ArgumentParser(description='Generate msem video thumbnail')

    parser.add_argument(
        '-o', '--output', help='Name of the output file (no extension)', default='thumbnail')

    parser.add_argument('config_json', help='Path to config json')

    args = parser.parse_args()
    configs = read_configs(args.config_json)
    img = create_thumbnail(configs)

    img.save(args.output + '.png')
