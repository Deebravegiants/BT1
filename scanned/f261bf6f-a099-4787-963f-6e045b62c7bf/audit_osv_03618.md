# [H] ALPINE-CVE-2026-34183

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34183
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34183
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.4.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.4.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.4.0 <3.5.7-r0

## Details
Issue summary: Remote peer may exhaust heap memory of the QUIC
server or client by flooding it with packets containing PATH_CHALLENGE
frames.

Impact summary: A malicious remote peer can cause an unbounded
memory allocation which can lead to an abnormal termination of the
application acting as a QUIC client or server and a Denial of Service.

A remote peer may exhaust heap memory by flooding the local
QUIC stack with PATH_CHALLENGE frames. The local QUIC stack
allocates a PATH_RESPONSE frame for every PATH_CHALLENGE it receives.
The allocated PATH_RESPONSE frame gets freed only when the remote
peer acknowledges reception of the PATH_RESPONSE frame which will
not be done by a malicious peer.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by
this issue. The QUIC stack is outside of OpenSSL FIPS module
boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34183
