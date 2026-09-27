# [H] ALPINE-CVE-2018-7254

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7254
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7254
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.4: `wavpack` — affected >=0 <5.1.0-r1
- Alpine:v3.5: `wavpack` — affected >=0 <5.1.0-r1
- Alpine:v3.6: `wavpack` — affected >=0 <5.1.0-r1
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r1
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r3
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r3

## Details
The ParseCaffHeaderConfig function of the cli/caff.c file of WavPack 5.1.0 allows a remote attacker to cause a denial-of-service (global buffer over-read), or possibly trigger a buffer overflow or incorrect memory allocation, via a maliciously crafted CAF file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7254
