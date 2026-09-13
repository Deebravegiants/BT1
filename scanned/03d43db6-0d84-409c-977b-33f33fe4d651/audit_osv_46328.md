# [M] Reusing authenticated connection when unauthenticated

## Summary
Severity: Medium
Advisory: CURL-CVE-2015-3143
Aliases: CVE-2015-3143
Published: 2015-04-22
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3143
Type: osv

## Details
libcurl keeps a pool of its last few connections around after use to
facilitate easy, convenient and completely transparent connection reuse for
applications.

When doing HTTP requests NTLM authenticated, the entire connection becomes
authenticated and not only the specific HTTP request which is otherwise how
HTTP works. This makes NTLM special and a subject for special treatment in the
code. With NTLM, once the connection is authenticated, no further
authentication is necessary until the connection gets closed.

libcurl's connection reuse logic selects an existing connection for reuse
when asked to do a request, and when asked to use NTLM libcurl have to pick a
connection with matching credentials only.

If a connection was first setup and used for an NTLM HTTP request with a
specific set of credentials, that same connection could later wrongly get
reused in a subsequent HTTP request that was made to the same host - but
without having any credentials set! Since an NTLM connection was already
authenticated due to how NTLM works, the subsequent request could then get
sent over the wrong connection appearing as the initial user.

This problem is similar to the previous problem known as
[CVE-2014-0015](https://curl.se/docs/CVE-2014-0015.html). The main difference
this time is that the subsequent request that wrongly reuse a connection does
not ask for NTLM authentication.
