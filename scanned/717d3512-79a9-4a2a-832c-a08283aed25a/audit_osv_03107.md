# [C] ALPINE-CVE-2024-45492

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-45492
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45492
Type: osv

## Affected
- Alpine:v3.17: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.18: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.19: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.20: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.21: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.22: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.23: `expat` — affected >=0 <2.6.3-r0
- Alpine:v3.24: `expat` — affected >=0 <2.6.3-r0

## Details
An issue was discovered in libexpat before 2.6.3. nextScaffoldPart in xmlparse.c can have an integer overflow for m_groupSize on 32-bit platforms (where UINT_MAX equals SIZE_MAX).

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45492
