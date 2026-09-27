# [H] ALPINE-CVE-2023-5869

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-5869
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5869
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
A flaw was found in PostgreSQL that allows authenticated database users to execute arbitrary code through missing overflow checks during SQL array value modification. This issue exists due to an integer overflow during array modification where a remote user can trigger the overflow by providing specially crafted data. This enables the execution of arbitrary code on the target system, allowing users to write arbitrary bytes to memory and extensively read the server's memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5869
