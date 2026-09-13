# [M] ALPINE-CVE-2022-32206

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-32206
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32206
Type: osv

## Affected
- Alpine:v3.13: `curl` — affected >=0 <7.79.1-r2
- Alpine:v3.14: `curl` — affected >=0 <7.79.1-r2
- Alpine:v3.15: `curl` — affected >=0 <7.80.0-r2
- Alpine:v3.16: `curl` — affected >=0 <7.83.1-r2
- Alpine:v3.17: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.84.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.84.0-r0

## Details
curl < 7.84.0 supports "chained" HTTP compression algorithms, meaning that a serverresponse can be compressed multiple times and potentially with different algorithms. The number of acceptable "links" in this "decompression chain" was unbounded, allowing a malicious server to insert a virtually unlimited number of compression steps.The use of such a decompression chain could result in a "malloc bomb", makingcurl end up spending enormous amounts of allocated heap memory, or trying toand returning out of memory errors.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32206
