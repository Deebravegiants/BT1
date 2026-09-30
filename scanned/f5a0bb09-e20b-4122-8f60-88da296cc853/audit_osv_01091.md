# [M] ALPINE-CVE-2018-19841

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19841
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19841
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r7
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r7
- Alpine:v3.6: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r7
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r7

## Details
The function WavpackVerifySingleBlock in open_utils.c in libwavpack.a in WavPack through 5.1.0 allows attackers to cause a denial-of-service (out-of-bounds read and application crash) via a crafted WavPack Lossless Audio file, as demonstrated by wvunpack.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19841
