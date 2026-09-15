# [H] ALPINE-CVE-2020-15166

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15166
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15166
Type: osv

## Affected
- Alpine:v3.10: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.11: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.12: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.13: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.14: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.15: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.16: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.17: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.18: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.19: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.20: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.21: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.22: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.23: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.24: `zeromq` — affected >=0 <4.3.3-r0
- Alpine:v3.9: `zeromq` — affected >=0 <4.3.3-r0

## Details
In ZeroMQ before version 4.3.3, there is a denial-of-service vulnerability. Users with TCP transport public endpoints, even with CURVE/ZAP enabled, are impacted. If a raw TCP socket is opened and connected to an endpoint that is fully configured with CURVE/ZAP, legitimate clients will not be able to exchange any message. Handshakes complete successfully, and messages are delivered to the library, but the server application never receives them. This is patched in version 4.3.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15166
