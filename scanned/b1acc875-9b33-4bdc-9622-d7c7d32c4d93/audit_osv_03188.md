# [M] ALPINE-CVE-2025-12818

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-12818
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-12818
Type: osv

## Affected
- Alpine:v3.19: `postgresql15` — affected >=0 <15.15-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.15-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.11-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.11-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.11-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.11-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.7-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.7-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.7-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.7-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.1-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.1-r0

## Details
Integer wraparound in multiple PostgreSQL libpq client library functions allows an application input provider or network peer to cause libpq to undersize an allocation and write out-of-bounds by hundreds of megabytes.  This results in a segmentation fault for the application using libpq.  Versions before PostgreSQL 18.1, 17.7, 16.11, 15.15, 14.20, and 13.23 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-12818
