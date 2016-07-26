# focusbrowser
A teeny tiny web browser designed to only show a few whitelisted pages.


Mouse middle click on links opens them in new windows. To open a completely different page in focusbrowser than the one active, start a new instance with that url as a terminal argument.

Cookies are loaded on startup and saved on quit. Beware that this might overwrite stuff if you have multiple instances open.


## Config
On startup a JSON config is placed in `$HOME/.config/focusbrowser`. The `default url` option is the url (including `http://`) that will be loaded if on startup if nothing else is specified. The `whitelist regexes` is a list of regular expressions for urls that should be allowed. Only websites whose urls match at least one of the regexes will be loaded (including when clicking on links)

## Commandline options
If you want to open another page than the default, simply pass that as an terminal argument and it will be loaded on startup, provided it is whitelisted.
