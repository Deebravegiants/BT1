# [H] ALPINE-CVE-2016-4074

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4074
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4074
Type: osv

## Affected
- Alpine:v3.10: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.11: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.12: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.13: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.14: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.15: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.16: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.17: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.18: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.19: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.20: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.21: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.22: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.23: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.24: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.4: `jq` — affected >=0 <1.5-r2
- Alpine:v3.5: `jq` — affected >=0 <1.5-r4
- Alpine:v3.6: `jq` — affected >=0 <1.5-r4
- Alpine:v3.7: `jq` — affected >=0 <1.5-r5
- Alpine:v3.8: `jq` — affected >=0 <1.6_rc1-r0
- Alpine:v3.9: `jq` — affected >=0 <1.6_rc1-r0

## Details
The jv_dump_term function in jq 1.5 allows remote attackers to cause a denial of service (stack consumption and application crash) via a crafted JSON file. This issue has been fixed in jq 1.6_rc1-r0.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4074
