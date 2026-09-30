# [H] ALPINE-CVE-2025-24928

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-24928
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-24928
Type: osv

## Affected
- Alpine:v3.18: `libxml2` — affected >=2.13.0 <2.11.8-r1
- Alpine:v3.19: `libxml2` — affected >=2.13.0 <2.11.8-r1
- Alpine:v3.20: `libxml2` — affected >=2.13.0 <2.12.7-r1
- Alpine:v3.21: `libxml2` — affected >=2.13.0 <2.13.4-r4
- Alpine:v3.22: `libxml2` — affected >=2.13.0 <2.13.6-r0
- Alpine:v3.23: `libxml2` — affected >=2.13.0 <2.13.6-r0
- Alpine:v3.24: `libxml2` — affected >=2.13.0 <2.13.6-r0

## Details
libxml2 before 2.12.10 and 2.13.x before 2.13.6 has a stack-based buffer overflow in xmlSnprintfElements in valid.c. To exploit this, DTD validation must occur for an untrusted document or untrusted DTD. NOTE: this is similar to CVE-2017-9047.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-24928
