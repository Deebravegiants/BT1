# [M] ALPINE-CVE-2026-6470

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-6470
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6470
Type: osv

## Affected
- Alpine:v3.21: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.5-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.5-r0

## Details
Missing authorization in PostgreSQL DDL commands allows an object creator to achieve denial of service against ALTER and DROP of the type, via creating a dependency on the type.  Many DDL operations did check the privilege, but assigning a range subtype and referencing the type from an SQL expression did not.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6470
