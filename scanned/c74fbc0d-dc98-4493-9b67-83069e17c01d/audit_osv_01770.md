# [H] ALPINE-CVE-2020-14360

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14360
Ecosystem: Alpine:v3.12
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14360
Type: osv

## Affected
- Alpine:v3.12: `xorg-server` — affected >=0 <1.20.10-r0

## Details
A flaw was found in the X.Org Server before version 1.20.10. An out-of-bounds access in the XkbSetMap function may lead to a privilege escalation vulnerability. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14360
