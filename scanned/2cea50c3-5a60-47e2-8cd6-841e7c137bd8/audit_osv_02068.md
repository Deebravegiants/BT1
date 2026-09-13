# [H] ALPINE-CVE-2021-20240

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-20240
Ecosystem: Alpine:v3.11, Alpine:v3.12
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20240
Type: osv

## Affected
- Alpine:v3.11: `gdk-pixbuf` — affected >=0 <2.40.0-r1
- Alpine:v3.12: `gdk-pixbuf` — affected >=0 <2.40.0-r3

## Details
A flaw was found in gdk-pixbuf in versions before 2.42.0. An integer wraparound leading to an out of bounds write can occur when a crafted GIF image is loaded. An attacker may cause applications to crash or could potentially execute code on the victim system. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20240
