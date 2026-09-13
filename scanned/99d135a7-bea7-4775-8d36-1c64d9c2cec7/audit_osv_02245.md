# [M] ALPINE-CVE-2021-3537

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3537
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3537
Type: osv

## Affected
- Alpine:v3.10: `libxml2` — affected >=0 <2.9.9-r5
- Alpine:v3.11: `libxml2` — affected >=0 <2.9.10-r5
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.10-r6
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.10-r7
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.11-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.11-r0

## Details
A vulnerability found in libxml2 in versions before 2.9.11 shows that it did not propagate errors while parsing XML mixed content, causing a NULL dereference. If an untrusted XML document was parsed in recovery mode and post-validated, the flaw could be used to crash the application. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3537
