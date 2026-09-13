# [M] ALPINE-CVE-2016-10170

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10170
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10170
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.2: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.3: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.4: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.5: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.6: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r0
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r0

## Details
The WriteCaffHeader function in cli/caff.c in Wavpack before 5.1.0 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted WV file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10170
