# [H] ALPINE-CVE-2018-6951

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-6951
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6951
Type: osv

## Affected
- Alpine:v3.10: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.11: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.12: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.13: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.14: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.15: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.16: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.17: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.18: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.19: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.20: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.21: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.22: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.23: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.24: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.4: `patch` — affected >=0 <2.7.5-r2
- Alpine:v3.5: `patch` — affected >=0 <2.7.5-r2
- Alpine:v3.6: `patch` — affected >=0 <2.7.5-r2
- Alpine:v3.7: `patch` — affected >=0 <2.7.5-r2
- Alpine:v3.8: `patch` — affected >=0 <2.7.6-r2
- Alpine:v3.9: `patch` — affected >=0 <2.7.6-r2

## Details
An issue was discovered in GNU patch through 2.7.6. There is a segmentation fault, associated with a NULL pointer dereference, leading to a denial of service in the intuit_diff_type function in pch.c, aka a "mangled rename" issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6951
