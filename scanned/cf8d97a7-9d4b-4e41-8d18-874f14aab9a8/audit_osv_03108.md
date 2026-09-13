# [H] ALPINE-CVE-2024-45624

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-45624
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45624
Type: osv

## Affected
- Alpine:v3.21: `pgpool` — affected >=0 <4.5.4-r0
- Alpine:v3.22: `pgpool` — affected >=0 <4.5.4-r0
- Alpine:v3.23: `pgpool` — affected >=0 <4.5.4-r0
- Alpine:v3.24: `pgpool` — affected >=0 <4.5.4-r0

## Details
Exposure of sensitive information due to incompatible policies issue exists in Pgpool-II. If a database user accesses a query cache, table data unauthorized for the user may be retrieved.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45624
