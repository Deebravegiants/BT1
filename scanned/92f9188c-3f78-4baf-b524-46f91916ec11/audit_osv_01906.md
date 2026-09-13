# [H] ALPINE-CVE-2020-25712

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25712
Ecosystem: Alpine:v3.12
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25712
Type: osv

## Affected
- Alpine:v3.12: `xorg-server` — affected >=0 <1.20.10-r0

## Details
A flaw was found in xorg-x11-server before 1.20.10. A heap-buffer overflow in XkbSetDeviceInfo may lead to a privilege escalation vulnerability. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25712
