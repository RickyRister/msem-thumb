# MSEM Thumbnail Generator

This project is meant to automatically generate thumbnails for MSEM commentary videos.

Currently it just automates the downloading of card images from the msem2 website.

## cardimgdl

`cardimgdl.py` can be run as a standalone script to download a card image from the command line.
No more having to go to instigator and look up the card and then right clicking the image and then looking through your download folder!

```
usage: cardimgdl.py -c CARDXML cardname

positional arguments:
  cardname              Name of the card, as it appears on Cockatrice

options:
  -h, --help            show this help message and exit
  -c, --cardxml CARDXML
                        Path to cards.xml
```

`cardimgdl.py` needs to know the path to your `cards.xml`, as it will use that to figure out the image url for the card.
You should be able to find `cards.xml` in your Cockatrice folder.
If you have multiple Cockatrice portables installed, make sure you're pointing to the msem one.

You may want to create an alias for `cardimgdl` that has `-c` already set. 
