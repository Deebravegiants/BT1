# [C] ALPINE-CVE-2016-7951

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7951
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7951
Type: osv

## Affected
- Alpine:v3.2: `libxtst` — affected >=0 <1.2.2-r1
- Alpine:v3.3: `libxtst` — affected >=0 <1.2.2-r1

## Details
Multiple integer overflows in X.org libXtst before 1.2.3 allow remote X servers to trigger out-of-bounds memory access operations by leveraging the lack of range checks.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7951
