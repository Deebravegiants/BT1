# [M] Negotiate not treated as connection-oriented

## Summary
Severity: Medium
Advisory: CURL-CVE-2015-3148
Aliases: CVE-2015-3148
Published: 2015-04-22
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3148
Type: osv

## Details
libcurl keeps a pool of its last few connections around after use to
facilitate easy, convenient and completely transparent connection reuse for
applications.

When doing HTTP requests Negotiate authenticated, the entire connection may
become authenticated and not only the specific HTTP request which is otherwise
how HTTP works, as Negotiate can use NTLM under the hood. curl was not
adhering to this fact but would assume that such requests would also be
authenticated per request.

The net effect is that libcurl may end up reusing an authenticated Negotiate
connection and sending subsequent requests on it using new credentials, while
the connection remains authenticated with a previous initial credentials
setup.
