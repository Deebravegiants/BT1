# [M] ALPINE-CVE-2016-3189

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-3189
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3189
Type: osv

## Affected
- Alpine:v3.10: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.11: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.12: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.13: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.14: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.15: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.16: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.17: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.18: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.19: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.20: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.21: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.22: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.23: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.24: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.4: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.5: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.6: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.7: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.8: `bzip2` — affected >=0 <1.0.6-r5
- Alpine:v3.9: `bzip2` — affected >=0 <1.0.6-r5

## Details
Use-after-free vulnerability in bzip2recover in bzip2 1.0.6 allows remote attackers to cause a denial of service (crash) via a crafted bzip2 file, related to block ends set to before the start of the block.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3189
