# [M] ALPINE-CVE-2019-11498

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-11498
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11498
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r4
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r8

## Details
WavpackSetConfiguration64 in pack_utils.c in libwavpack.a in WavPack through 5.1.0 has a "Conditional jump or move depends on uninitialised value" condition, which might allow attackers to cause a denial of service (application crash) via a DFF file that lacks valid sample-rate data.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11498
