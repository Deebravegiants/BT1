# [H] ALPINE-CVE-2020-14346

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14346
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14346
Type: osv

## Affected
- Alpine:v3.10: `xorg-server` — affected >=0 <1.20.5-r2
- Alpine:v3.11: `xorg-server` — affected >=0 <1.20.6-r2
- Alpine:v3.12: `xorg-server` — affected >=0 <1.20.9-r0
- Alpine:v3.9: `xorg-server` — affected >=0 <1.20.3-r2

## Details
A flaw was found in xorg-x11-server before 1.20.9. An integer underflow in the X input extension protocol decoding in the X server may lead to arbitrary access of memory contents. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14346
