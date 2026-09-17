# [M] ALPINE-CVE-2026-1965

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-1965
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1965
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.10.6 <8.19.0-r0
- Alpine:v3.24: `curl` — affected >=7.10.6 <8.19.0-r0

## Details
libcurl can in some circumstances reuse the wrong connection when asked to do
an Negotiate-authenticated HTTP or HTTPS request.

libcurl features a pool of recent connections so that subsequent requests can
reuse an existing connection to avoid overhead.

When reusing a connection a range of criterion must first be met. Due to a
logical error in the code, a request that was issued by an application could
wrongfully reuse an existing connection to the same server that was
authenticated using different credentials. One underlying reason being that
Negotiate sometimes authenticates *connections* and not *requests*, contrary
to how HTTP is designed to work.

An application that allows Negotiate authentication to a server (that responds
wanting Negotiate) with `user1:password1` and then does another operation to
the same server also using Negotiate but with `user2:password2` (while the
previous connection is still alive) - the second request wrongly reused the
same connection and since it then sees that the Negotiate negotiation is
already made, it just sends the request over that connection thinking it uses
the user2 credentials when it is in fact still using the connection
authenticated for user1...

The set of authentication methods to use is set with  `CURLOPT_HTTPAUTH`.

Applications can disable libcurl's reuse of connections and thus mitigate this
problem, by using one of the following libcurl options to alter how
connections are or are not reused: `CURLOPT_FRESH_CONNECT`,
`CURLOPT_MAXCONNECTS` and `CURLMOPT_MAX_HOST_CONNECTIONS` (if using the
curl_multi API).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1965
