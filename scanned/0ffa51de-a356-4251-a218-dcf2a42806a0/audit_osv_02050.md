# [M] ALPINE-CVE-2021-20191

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-20191
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20191
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.9.0 <2.8.19-r0
- Alpine:v3.11: `ansible` — affected >=2.9.0 <2.9.18-r0
- Alpine:v3.12: `ansible` — affected >=2.9.0 <2.9.18-r0
- Alpine:v3.13: `ansible` — affected >=2.9.0 <2.10.7-r0
- Alpine:v3.14: `ansible` — affected >=2.9.0 <2.10.7-r0

## Details
A flaw was found in ansible. Credentials, such as secrets, are being disclosed in console log by default and not protected by no_log feature when using those modules. An attacker can take advantage of this information to steal those credentials. The highest threat from this vulnerability is to data confidentiality. Versions before ansible 2.9.18 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20191
