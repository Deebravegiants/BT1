# [C] ALPINE-CVE-2016-5407

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-5407
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5407
Type: osv

## Affected
- Alpine:v3.2: `libxv` — affected >=0 <1.0.10-r1
- Alpine:v3.3: `libxv` — affected >=0 <1.0.10-r2

## Details
The (1) XvQueryAdaptors and (2) XvQueryEncodings functions in X.org libXv before 1.0.11 allow remote X servers to trigger out-of-bounds memory access operations via vectors involving length specifications in received data.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5407
