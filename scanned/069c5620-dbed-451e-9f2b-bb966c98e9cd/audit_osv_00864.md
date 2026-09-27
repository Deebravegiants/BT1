# [M] ALPINE-CVE-2018-1000085

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1000085
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000085
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.4: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.5: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.4-r0

## Details
ClamAV version version 0.99.3 contains a Out of bounds heap memory read vulnerability in XAR parser, function xar_hash_check() that can result in Leaking of memory, may help in developing exploit chains.. This attack appear to be exploitable via The victim must scan a crafted XAR file. This vulnerability appears to have been fixed in after commit d96a6b8bcc7439fa7e3876207aa0a8e79c8451b6.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000085
