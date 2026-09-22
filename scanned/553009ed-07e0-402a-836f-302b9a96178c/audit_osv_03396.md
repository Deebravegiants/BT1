# [H] ALPINE-CVE-2025-8671

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-8671
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-8671
Type: osv

## Affected
- Alpine:v3.15: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.16: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.17: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.18: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.19: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.20: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.21: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.22: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.23: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.24: `lighttpd` — affected >=0 <0-r0
- Alpine:v3.22: `varnish` — affected >=0 <7.7.2-r0
- Alpine:v3.23: `varnish` — affected >=0 <7.7.2-r0
- Alpine:v3.24: `varnish` — affected >=0 <7.7.2-r0

## Details
A mismatch caused by client-triggered server-sent stream resets between HTTP/2 specifications and the internal architectures of some HTTP/2 implementations may result in excessive server resource consumption leading to denial-of-service (DoS).  By opening streams and then rapidly triggering the server to reset them—using malformed frames or flow control errors—an attacker can exploit incorrect stream accounting. Streams reset by the server are considered closed at the protocol level, even though backend processing continues. This allows a client to cause the server to handle an unbounded number of concurrent streams on a single connection. This CVE will be updated as affected product details are released.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-8671
