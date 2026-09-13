# [M] FTP wildcard out of bounds read

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-8817
Aliases: CVE-2017-8817
Published: 2017-11-29
Source: https://osv.dev/vulnerability/CURL-CVE-2017-8817
Type: osv

## Details
libcurl contains a read out of bounds flaw in the FTP wildcard function.

libcurl's FTP wildcard matching feature, which is enabled with the
`CURLOPT_WILDCARDMATCH` option can use a built-in wildcard function or a user
provided one. The built-in wildcard function has a flaw that makes it not
detect the end of the pattern string if it ends with an open bracket (`[`) but
instead it continues reading the heap beyond the end of the URL buffer that
holds the wildcard.

For applications that use HTTP(S) URLs, allow libcurl to handle redirects and
have FTP wildcards enabled, this flaw can be triggered by malicious servers
that can redirect clients to a URL using such a wildcard pattern.
