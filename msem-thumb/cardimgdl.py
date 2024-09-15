#!/usr/bin/env python3

'''
For downloading an image from a card name
'''
from argparse import ArgumentParser
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from urllib import request

MSEM_CARD_URL_FMT = 'http://mse-modern.com/msem2/images/{setcode}/{setnum}.jpg '


def get_img_url_msem(cardname: str, cards_xml: str | Element) -> str:
    '''
    Gets the image url of the card on the msem2 site

    Args:
        cardname: The card name, as it appears in cards.xml (aka on Cockatrice)
        cards_xml: cards.xml, either as a path or loaded into an Element
    '''
    node = find_card_in_xml(cardname, cards_xml)
    setcode = node.find('./set').text
    setnum = node.find('./set').get('num')
    return MSEM_CARD_URL_FMT.format(setcode=setcode, setnum=setnum)


def find_card_in_xml(cardname: str, cards_xml: str | Element) -> Element:
    '''
    Searches cards.xml for the card. Raises exception if not found
    Args:
        cardname: The card name, as it appears in cards.xml (aka on Cockatrice)
        cards_xml: cards.xml, either as a path or loaded into an Element

    Returns:
        The xml node for that card. The node is be expected to have the following structure:
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
    if not isinstance(cards_xml , Element):
        with open(cards_xml) as xml_file:
            etree = ElementTree.parse(xml_file)
            cards_xml = etree.getroot()

    # find the <card> node of the cardname
    card_node: Element | None = cards_xml.find(f'.//card[name="{cardname}"]')

    if card_node is None:
        raise ValueError(f'[{cardname}] not found in cards.xml.')

    return card_node


if __name__ == "__main__":
    parser = ArgumentParser(description='Download card images from the msem website')

    parser.add_argument('-c', '--cardxml', type=str, required=True, help='Path to cards.xml')
    parser.add_argument('cardname', help='Name of the card, as it appears on Cockatrice')

    args = parser.parse_args()

    url = get_img_url_msem(args.cardname, args.cardxml)

    request.urlretrieve(url, f'{args.cardname}.jpg')
    
