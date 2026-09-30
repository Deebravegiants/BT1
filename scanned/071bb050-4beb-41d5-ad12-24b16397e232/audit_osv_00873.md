# [C] ALPINE-CVE-2018-1000300

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-1000300
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000300
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.11: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.12: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.13: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.14: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.15: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.16: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.17: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.18: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.19: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.20: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.21: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.22: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.23: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.24: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.4: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.5: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.6: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.7: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.8: `curl` — affected >=7.54.1 <7.60.0-r0
- Alpine:v3.9: `curl` — affected >=7.54.1 <7.60.0-r0

## Details
curl version curl 7.54.1 to and including curl 7.59.0 contains a CWE-122: Heap-based Buffer Overflow vulnerability in denial of service and more that can result in curl might overflow a heap based memory buffer when closing down an FTP connection with very long server command replies.. This vulnerability appears to have been fixed in curl < 7.54.1 and curl >= 7.60.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000300
