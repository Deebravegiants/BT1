# [M] ALPINE-CVE-2019-1010315

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1010315
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1010315
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r4
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r8

## Details
WavPack 5.1 and earlier is affected by: CWE 369: Divide by Zero. The impact is: Divide by zero can lead to sudden crash of a software/service that tries to parse a .wav file. The component is: ParseDsdiffHeaderConfig (dsdiff.c:282). The attack vector is: Maliciously crafted .wav file. The fixed version is: After commit https://github.com/dbry/WavPack/commit/4c0faba32fddbd0745cbfaf1e1aeb3da5d35b9fc.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1010315
