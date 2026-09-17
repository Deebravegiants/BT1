# [H] ALPINE-CVE-2021-3472

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3472
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3472
Type: osv

## Affected
- Alpine:v3.10: `xorg-server` — affected >=0 <1.20.5-r3
- Alpine:v3.11: `xorg-server` — affected >=0 <1.20.6-r3
- Alpine:v3.12: `xorg-server` — affected >=0 <1.20.10-r1

## Details
A flaw was found in xorg-x11-server in versions before 1.20.11. An integer underflow can occur in xserver which can lead to a local privilege escalation. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3472
