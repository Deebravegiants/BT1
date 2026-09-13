# [C] ALPINE-CVE-2019-19330

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-19330
Ecosystem: Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19330
Type: osv

## Affected
- Alpine:v3.8: `haproxy` — affected >=0 <1.8.23
- Alpine:v3.9: `haproxy` — affected >=0 <1.8.23-r0

## Details
The HTTP/2 implementation in HAProxy before 2.0.10 mishandles headers, as demonstrated by carriage return (CR, ASCII 0xd), line feed (LF, ASCII 0xa), and the zero character (NUL, ASCII 0x0), aka Intermediary Encapsulation Attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19330
