# [M] wrong reuse of HTTP Negotiate connection

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-5545
Aliases: CVE-2026-5545
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CURL-CVE-2026-5545
Type: osv

## Details
libcurl might in some circumstances reuse the wrong connection when asked to
do an authenticated HTTP(S) request after a Negotiate-authenticated one, when
both use the same host.

libcurl features a pool of recent connections so that subsequent requests can
reuse an existing connection to avoid overhead.

When reusing a connection a range of criteria must be met. Due to a logical
error in the code, a request that was issued by an application could
wrongfully reuse an existing connection to the same server that was
authenticated using different credentials.

An application that first uses Negotiate authentication to a server with
`user1:password1` and then does another operation to the same server asking
for any authentication method but for `user2:password2` (while the previous
connection is still alive) - the second request gets confused and wrongly
reuses the same connection and sends the new request over that connection
thinking it uses a mix of user1's and user2's credentials when it is in fact
still using the connection authenticated for user1...
