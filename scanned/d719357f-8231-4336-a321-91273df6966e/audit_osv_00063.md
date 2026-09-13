# [H] ALPINE-CVE-2016-10369

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-10369
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10369
Type: osv

## Affected
- Alpine:v3.10: `lxterminal` — affected >=0 <0.3.0-r1
- Alpine:v3.11: `lxterminal` — affected >=0 <0.3.0-r1
- Alpine:v3.6: `lxterminal` — affected >=0 <0.3.0-r1
- Alpine:v3.7: `lxterminal` — affected >=0 <0.3.0-r1
- Alpine:v3.8: `lxterminal` — affected >=0 <0.3.0-r1
- Alpine:v3.9: `lxterminal` — affected >=0 <0.3.0-r1

## Details
unixsocket.c in lxterminal through 0.3.0 insecurely uses /tmp for a socket file, allowing a local user to cause a denial of service (preventing terminal launch), or possibly have other impact (bypassing terminal access control).

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10369
