# [H] ALPINE-CVE-2017-9671

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9671
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9671
Type: osv

## Affected
- Alpine:v3.10: `apk-tools` — affected >=0 <2.7.2-r0
- Alpine:v3.11: `apk-tools` — affected >=0 <2.7.2-r0
- Alpine:v3.12: `apk-tools` — affected >=0 <2.7.2-r0
- Alpine:v3.13: `apk-tools` — affected >=0 <2.7.2-r0

## Details
A heap overflow in apk (Alpine Linux's package manager) allows a remote attacker to cause a denial of service, or achieve code execution, by crafting a malicious APKINDEX.tar.gz file with a bad pax header block.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9671
