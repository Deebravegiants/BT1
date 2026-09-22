# [M] ALPINE-CVE-2016-2107

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-2107
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2107
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r0

## Details
The AES-NI implementation in OpenSSL before 1.0.1t and 1.0.2 before 1.0.2h does not consider memory allocation during a certain padding check, which allows remote attackers to obtain sensitive cleartext information via a padding-oracle attack against an AES CBC session. NOTE: this vulnerability exists because of an incorrect fix for CVE-2013-0169.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2107
