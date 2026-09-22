# [M] ALPINE-CVE-2018-19840

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19840
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19840
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r7
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r7
- Alpine:v3.6: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r7
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r7

## Details
The function WavpackPackInit in pack_utils.c in libwavpack.a in WavPack through 5.1.0 allows attackers to cause a denial-of-service (resource exhaustion caused by an infinite loop) via a crafted wav audio file because WavpackSetConfiguration64 mishandles a sample rate of zero.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19840
