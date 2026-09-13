# [M] ALPINE-CVE-2026-5545

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-5545
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5545
Type: osv

## Affected
- Alpine:v3.22: `curl` — affected >=7.10.6 <8.14.1-r3
- Alpine:v3.23: `curl` — affected >=7.10.6 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.10.6 <8.20.0-r0

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

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5545
