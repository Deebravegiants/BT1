# [M] ALPINE-CVE-2012-6702

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2012-6702
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2012-6702
Type: osv

## Affected
- Alpine:v3.2: `expat` — affected >=0 <2.2.0-r0
- Alpine:v3.3: `expat` — affected >=0 <2.2.0-r0
- Alpine:v3.4: `expat` — affected >=0 <2.2.0-r0

## Details
Expat, when used in a parser that has not called XML_SetHashSalt or passed it a seed of 0, makes it easier for context-dependent attackers to defeat cryptographic protection mechanisms via vectors involving use of the srand function.

## References
- https://security.alpinelinux.org/vuln/CVE-2012-6702
