# [M] hostname out of boundary memory access

## Summary
Severity: Medium
Advisory: CURL-CVE-2015-3144
Aliases: CVE-2015-3144
Published: 2015-04-22
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3144
Type: osv

## Details
There is a private function in libcurl called `fix_hostname()` that removes a
trailing dot from the hostname if there is one. The function is called after
the hostname has been extracted from the URL libcurl has been told to act on.

If a URL is given with a zero-length hostname, like in "http://:80" or ":80",
`fix_hostname()` indexes the hostname pointer with a -1 offset (as it blindly
assumes a non-zero length) and both read and assign that address.

At best, this gets unnoticed but can also lead to a crash or worse. We have
not researched further what kind of malicious actions that potentially this
could be used for.
