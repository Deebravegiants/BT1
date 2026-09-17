# [M] ALPINE-CVE-2019-1010319

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1010319
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1010319
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r4
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r8
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r8

## Details
WavPack 5.1.0 and earlier is affected by: CWE-457: Use of Uninitialized Variable. The impact is: Unexpected control flow, crashes, and segfaults. The component is: ParseWave64HeaderConfig (wave64.c:211). The attack vector is: Maliciously crafted .wav file. The fixed version is: After commit https://github.com/dbry/WavPack/commit/33a0025d1d63ccd05d9dbaa6923d52b1446a62fe.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1010319
