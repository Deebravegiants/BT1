# [M] ALPINE-CVE-2023-5868

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-5868
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5868
Type: osv

## Affected
- Alpine:v3.15: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.10-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.5-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.1-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.1-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.1-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.1-r0

## Details
A memory disclosure vulnerability was found in PostgreSQL that allows remote users to access sensitive information by exploiting certain aggregate function calls with 'unknown'-type arguments. Handling 'unknown'-type values from string literals without type designation can disclose bytes, potentially revealing notable and confidential information. This issue exists due to excessive data output in aggregate function calls, enabling remote users to read some portion of system memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5868
