# [H] lingering HTTP credentials in connection reuse

## Summary
Severity: High
Advisory: CURL-CVE-2015-3236
Aliases: CVE-2015-3236
Published: 2015-06-17
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3236
Type: osv

## Details
libcurl can wrongly send HTTP credentials when reusing connections.

libcurl allows applications to set credentials for the upcoming transfer with
HTTP Basic authentication, like with `CURLOPT_USERPWD` for example. Name and
password. Like all other libcurl options the credentials are sticky and are
kept associated with the "handle" until something is made to change the
situation.

Further, libcurl offers a `curl_easy_reset()` function that resets a handle
back to its pristine state in terms of all settable options. A reset is of
course also supposed to clear the credentials. A reset is typically used to
clear up the handle and prepare it for a new, possibly unrelated, transfer.

Within such a handle, libcurl can also store a set of previous connections in
case a second transfer is requested to a hostname for which an existing
connection is already kept alive.

With this flaw present, using the handle even after a reset would make libcurl
accidentally use those credentials in a subsequent request if done to the same
hostname and connection as was previously accessed.

An example case would be first requesting a password protected resource from
one section of a website, and then do a second request of a public resource
from a completely different part of the site without authentication. This flaw
would then inadvertently leak the credentials in the second request.
