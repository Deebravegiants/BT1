# [C] ALPINE-CVE-2019-13132

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-13132
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13132
Type: osv

## Affected
- Alpine:v3.10: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.11: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.12: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.13: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.14: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.15: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.16: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.17: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.18: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.19: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.20: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.21: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.22: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.23: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.24: `zeromq` — affected >=0 <4.3.2-r0
- Alpine:v3.7: `zeromq` — affected >=0 <4.2.5-r1
- Alpine:v3.8: `zeromq` — affected >=0 <4.2.5-r1
- Alpine:v3.9: `zeromq` — affected >=0 <4.3.2-r0

## Details
In ZeroMQ libzmq before 4.0.9, 4.1.x before 4.1.7, and 4.2.x before 4.3.2, a remote, unauthenticated client connecting to a libzmq application, running with a socket listening with CURVE encryption/authentication enabled, may cause a stack overflow and overwrite the stack with arbitrary data, due to a buffer overflow in the library. Users running public servers with the above configuration are highly encouraged to upgrade as soon as possible, as there are no known mitigations.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13132
