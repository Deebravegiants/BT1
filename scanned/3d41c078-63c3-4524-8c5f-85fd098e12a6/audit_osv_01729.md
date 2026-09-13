# [M] ALPINE-CVE-2020-12400

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-12400
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12400
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.55-r0
- Alpine:v3.19: `nss` — affected >=0 <3.55-r0
- Alpine:v3.20: `nss` — affected >=0 <3.55-r0
- Alpine:v3.21: `nss` — affected >=0 <3.55-r0
- Alpine:v3.22: `nss` — affected >=0 <3.55-r0
- Alpine:v3.23: `nss` — affected >=0 <3.55-r0
- Alpine:v3.24: `nss` — affected >=0 <3.55-r0

## Details
When converting coordinates from projective to affine, the modular inversion was not performed in constant time, resulting in a possible timing-based side channel attack. This vulnerability affects Firefox < 80 and Firefox for Android < 80.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12400
