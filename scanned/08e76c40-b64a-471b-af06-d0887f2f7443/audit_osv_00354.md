# [M] ALPINE-CVE-2017-1000099

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-1000099
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000099
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.3: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.4: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.5: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.7: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.8: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.9: `curl` — affected >=0 <7.55.0-r0

## Details
When asking to get a file from a file:// URL, libcurl provides a feature that outputs meta-data about the file using HTTP-like headers. The code doing this would send the wrong buffer to the user (stdout or the application's provide callback), which could lead to other private data from the heap to get inadvertently displayed. The wrong buffer was an uninitialized memory area allocated on the heap and if it turned out to not contain any zero byte, it would continue and display the data following that buffer in memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000099
