# [M] ALPINE-CVE-2018-10539

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-10539
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10539
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r6
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r6
- Alpine:v3.4: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.5: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.6: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r6
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r6

## Details
An issue was discovered in WavPack 5.1.0 and earlier for DSDiff input. Out-of-bounds writes can occur because ParseDsdiffHeaderConfig in dsdiff.c does not validate the sizes of unknown chunks before attempting memory allocation, related to a lack of integer-overflow protection within a bytes_to_copy calculation and subsequent malloc call, leading to insufficient memory allocation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10539
