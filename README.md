# MSEM Thumbnail Generator

Automatically generate thumbnails for MSEM commentary videos.

Currently this tool can only generate thumbnails in the format of my MSEM commentary video thumbnails.
Don't know if I'll add more configuration options in the future.

## msem_thumb

```
usage: msem_thumb.py [-h] config_json

positional arguments:
  config_json  Path to config json

options:
  -h, --help   show this help message and exit
```

The config json is used to configure the parameters of the thumbnail.
See the `config.json` in `example` for an example of the json.

Most properties in the json are optional. 
If a property for an element is missing, then the script will simply skip generating that element.

This script uses `cards.xml` to figure out urls from card names.
The `cardsXmlPath` property in the config json is mandatory.
See the `cardimgdl` part of the README for more details about the `cards.xml`.

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
