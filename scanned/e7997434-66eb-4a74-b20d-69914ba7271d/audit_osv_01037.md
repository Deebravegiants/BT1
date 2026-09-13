# [C] ALPINE-CVE-2018-16840

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-16840
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16840
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.11: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.12: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.13: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.14: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.15: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.16: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.17: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.18: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.19: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.20: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.21: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.22: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.23: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.24: `curl` — affected >=7.59.0 <7.62.0-r0
- Alpine:v3.5: `curl` — affected >=7.59.0 <7.61.1-r1
- Alpine:v3.6: `curl` — affected >=7.59.0 <7.61.1-r1
- Alpine:v3.7: `curl` — affected >=7.59.0 <7.61.1-r1
- Alpine:v3.8: `curl` — affected >=7.59.0 <7.61.1-r1
- Alpine:v3.9: `curl` — affected >=7.59.0 <7.62.0-r0

## Details
A heap use-after-free flaw was found in curl versions from 7.59.0 through 7.61.1 in the code related to closing an easy handle. When closing and cleaning up an 'easy' handle in the `Curl_close()` function, the library code first frees a struct (without nulling the pointer) and might then subsequently erroneously write to a struct field within that already freed struct.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16840
