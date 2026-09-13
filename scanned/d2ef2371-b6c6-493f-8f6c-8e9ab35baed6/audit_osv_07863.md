# [M] reuse of wrong HTTP NTLM connection

## Summary
Severity: Medium
Advisory: CURL-CVE-2014-0015
Aliases: CVE-2014-0015
Published: 2014-01-29
Source: https://osv.dev/vulnerability/CURL-CVE-2014-0015
Type: osv

## Details
libcurl can in some circumstances reuse the wrong connection when asked to
do an NTLM-authenticated HTTP or HTTPS request.

libcurl features a pool of recent connections so that subsequent requests
can reuse an existing connection to avoid overhead.

When reusing a connection a range of criterion must first be met. Due to a
logical error in the code, a request that was issued by an application could
wrongfully reuse an existing connection to the same server that was
authenticated using different credentials. One underlying reason being that
NTLM authenticates connections and not requests, contrary to how HTTP is
designed to work and how other authentication methods work.

An application that allows NTLM and another auth method (the bug only triggers
if more than one auth method is asked for) to a server (that responds wanting
NTLM) with user1:password1 and then does another operation to the same server
with user2:password2 (when the previous connection was left alive) - the
second request reuses the same connection and since it then sees that the
NTLM negotiation is already made, it sends the request over that connection
thinking it uses the user2 credentials when it is in fact still using
the connection authenticated for user1...

The set of auth methods to use is set with `CURLOPT_HTTPAUTH`.

Two common auth defines in libcurl are `CURLAUTH_ANY` and `CURLAUTH_ANYSAFE`.
Both of them ask for NTLM and other methods and can therefore trigger this
problem.

Applications can disable libcurl's reuse of connections and thus mitigate
this problem, by using one of the following libcurl options to alter how
connections are or are not reused: `CURLOPT_FRESH_CONNECT`,
`CURLOPT_MAXCONNECTS` and `CURLMOPT_MAX_HOST_CONNECTIONS` (if using the
curl_multi API).
