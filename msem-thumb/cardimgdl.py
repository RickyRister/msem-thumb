#!/usr/bin/env python3

'''
For downloading an image from a card name
'''
import os
from argparse import ArgumentParser
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from urllib import request
from functools import cache

MSEM_CARD_URL_FMT = 'http://mse-modern.com/msem2/images/{setcode}/{setnum}.jpg '


class CardNotFound(Exception):
    '''Raised when the given card name is not found in the cards.xml
    '''

    def __init__(self, cardname: str):
        self.cardname = cardname
        super().__init__(f'[{self.cardname}] not found in cards.xml.')


@cache
def load_cards_xml(cards_xml_path: str) -> Element:
    '''Reads the cards.xml.
    Does null checking and expands the users in the path.

    Caches the result so the xml doesn't get parsed multiple times.
    DO NOT modify the Element that gets returned.
    '''
    if cards_xml_path is None:
        raise ValueError('Path to cards.xml not given')
    cards_xml_path = os.path.expanduser(cards_xml_path)
    with open(cards_xml_path) as xml_file:
        etree = ElementTree.parse(xml_file)
        return etree.getroot()


def find_img_url(cardname: str, cards_xml: str | Element, img_url_format: str = MSEM_CARD_URL_FMT) -> str:
    '''
    Gets the image url of the card.

    Args:
        cardname: The card name, as it appears in cards.xml (aka on Cockatrice)
        cards_xml: cards.xml, either as a path or loaded into an Element
        img_url_format: url format corresponding to the card's image
    '''
    node = find_card_in_xml(cardname, cards_xml)
    setcode = node.find('./set').text
    setnum = node.find('./set').get('num')
    return img_url_format.format(setcode=setcode, setnum=setnum)


def find_card_in_xml(cardname: str, cards_xml: str | Element) -> Element:
    '''
    Searches cards.xml for the card. Raises exception if not found
    Args:
        cardname: The card name, as it appears in cards.xml (aka on Cockatrice)
        cards_xml: cards.xml, either as a path or loaded into an Element

    Returns:
        The xml node for that card. The node is expected to have the following structure:
            <card>
                <name>Plains_TWR</name>
                <text>({T}: Add {W}.)</text>
                <prop>
                    <layout>normal</layout>
                    <side>front</side>
                    <type>Basic Land — Plains</type>
                    <coloridentity>W</coloridentity>
                    <cmc>0</cmc>
                    <maintype>Land</maintype>
                </prop>
                <set num="250" rarity="basic land">TWR</set>
                <tablerow>0</tablerow>
            </card>
    '''
    # load cards.xml if it's a path
    if not isinstance(cards_xml, Element):
        cards_xml = load_cards_xml(cards_xml)

    # find the <card> node of the cardname
    card_node: Element | None = cards_xml.find(f'.//card[name="{cardname}"]')

    if card_node is None:
        raise CardNotFound(cardname)

    return card_node


if __name__ == "__main__":
    parser = ArgumentParser(description='Download card images from the msem website')

    parser.add_argument('-c', '--cardxml', type=str, required=True, help='Path to cards.xml')
    parser.add_argument('cardnames', nargs='*',
                        help='Name(s) of the card(s), as they appear on Cockatrice')

    args = parser.parse_args()

    fail_count: int = 0
    for cardname in args.cardnames:
        try:
            url = find_img_url(cardname, args.cardxml)
            request.urlretrieve(url, f'{cardname}.jpg')
            print(f'Succefully downloaded [{cardname}]')
        except CardNotFound as e:
            print(f'[{e.cardname}] not found in cards.xml; skipping...')
            fail_count += 1

    if fail_count > 0:
        print(f"Failed to find {fail_count} card(s) in cards.xml.")
        print("If you're certain the card names are correct, check that you have the cards.xml for the correct format loaded.")
