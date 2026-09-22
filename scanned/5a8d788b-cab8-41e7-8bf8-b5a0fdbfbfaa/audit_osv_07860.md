# [H] URL sanitization vulnerability

## Summary
Severity: High
Advisory: CURL-CVE-2012-0036
Aliases: CVE-2012-0036
Published: 2012-01-24
Source: https://osv.dev/vulnerability/CURL-CVE-2012-0036
Type: osv

## Details
curl is vulnerable to a data injection attack for certain protocols through
control characters embedded or percent-encoded in URLs.

When parsing URLs, libcurl's parser is liberal and only parses as little as
possible and lets as much as possible through as long as it can figure out
what to do.

In the specific process when libcurl extracts the file path part from a given
URL, it did not always verify the data or escape control characters properly
before it passed the file path on to the protocol-specific code that then
would use it for its protocol business.

This passing through of control characters could be exploited by someone who
would be able to pass in a handcrafted URL to libcurl. Lots of libcurl
using applications let users enter URLs in one form or another and not all
of these check the input carefully to prevent malicious ones.

A malicious user might pass in %0d%0a to get treated as CR LF by libcurl,
and by using this fact a user can trick for example a POP3 client to delete
a message instead of getting it or trick an SMTP server to send an
unintended message.

This vulnerability can be used to fool libcurl with the following protocols:
IMAP, POP3 and SMTP.

Both curl the command line tool and applications using the libcurl library
are vulnerable.
