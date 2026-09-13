# [H] SSL CBC IV vulnerability

## Summary
Severity: High
Advisory: CURL-CVE-2011-3389
Aliases: CVE-2011-3389, PSF-2011-3
Published: 2012-01-24
Source: https://osv.dev/vulnerability/CURL-CVE-2011-3389
Type: osv

## Details
curl is vulnerable to a SSL CBC IV vulnerability when built to use OpenSSL for
the SSL/TLS layer.

This vulnerability has been identified (CVE-2011-3389 aka the "BEAST" attack)
and is addressed by OpenSSL already as they have made a workaround to
mitigate the problem. When doing so, they figured out that some servers did
not work with the workaround and offered a way to disable it.

The bit used to disable the workaround was then added to the generic
`SSL_OP_ALL` bitmask that SSL clients may use to enable workarounds for better
compatibility with servers. libcurl uses the SSL_OP_ALL bitmask.

While `SSL_OP_ALL` is documented to enable "rather harmless" workarounds, it
does in this case effectively enable this security vulnerability again.
