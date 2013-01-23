# notify-webhook Pivotal Tracker Adaptation

notify-webhook is a [git](http://git.or.cz) post-receive hook script
that posts XML data to Pivotal Tracker's API. 

This project is a fork of [https://github.com/metajack/notify-webhook](https://github.com/metajack/notify-webhook) with very few changes to most of the content.

The base code implements the [GitHub](http://github.com) [Web hooks
API](http://github.com/guides/post-receive-hooks) as closely as
possible, allowing arbitrary git repositories to use webhook
capable services. At the moment, however, this fork only supports commits!

## Dependencies

[dict2xml2](https://github.com/bentasker/dict2xml2)


## Usage

To use notify-webhook-pivotal-tracker, just copy `notify-webhook-pivotal-tracker.py` to your
repository's `.git/hooks` dir and call it `post-receive`. Be sure to
set it executable with `chmod 755 post-receive` as well.


### Configuration

Configuration is handled through `git config`. We use sensible defaults
where possible.

Here's an example:

    git config hooks.webhookurl "http://www.pivotaltracker.com/services/v3/source_commits"
    git config meta.apikey YOUR API KEY


#### hooks.webhookurl
The URL to the webhook consumer - the commit details will be POSTed
here. The value above should be fine unless an update of the API is released


#### meta.url
The URL of your repository browser

Defaults to `None`


#### meta.commiturl
The URL of a commit in your repository browser. `%s` is replaced with
the SHA1 hash of the commit.  
Defaults to `meta.url+'/commit/%s'` or `None`


## License

This code is copyright (c) 2013 Ben Tasker

Original copyright (c) 2008 Jack Moffitt <jack@metajack.im> and
is available under the [GPLv3](http://www.gnu.org/licenses/gpl.html).
See `LICENSE.txt` for details.
