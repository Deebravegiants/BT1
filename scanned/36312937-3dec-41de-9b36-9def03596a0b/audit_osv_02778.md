# [M] ALPINE-CVE-2023-23916

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-23916
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-23916
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=7.57.0 <7.79.1-r5
- Alpine:v3.15: `curl` — affected >=7.57.0 <7.80.0-r6
- Alpine:v3.16: `curl` — affected >=7.57.0 <7.83.1-r6
- Alpine:v3.17: `curl` — affected >=7.57.0 <7.87.0-r2
- Alpine:v3.18: `curl` — affected >=7.57.0 <7.88.0-r0
- Alpine:v3.19: `curl` — affected >=7.57.0 <7.88.0-r0
- Alpine:v3.20: `curl` — affected >=7.57.0 <7.88.0-r0
- Alpine:v3.21: `curl` — affected >=7.57.0 <7.88.0-r0
- Alpine:v3.22: `curl` — affected >=7.57.0 <7.88.0-r0
- Alpine:v3.23: `curl` — affected >=7.57.0 <7.88.0-r0
- Alpine:v3.24: `curl` — affected >=7.57.0 <7.88.0-r0

## Details
An allocation of resources without limits or throttling vulnerability exists in curl <v7.88.0 based on the "chained" HTTP compression algorithms, meaning that a server response can be compressed multiple times and potentially with differentalgorithms. The number of acceptable "links" in this "decompression chain" wascapped, but the cap was implemented on a per-header basis allowing a maliciousserver to insert a virtually unlimited number of compression steps simply byusing many headers. The use of such a decompression chain could result in a "malloc bomb", making curl end up spending enormous amounts of allocated heap memory, or trying to and returning out of memory errors.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-23916
