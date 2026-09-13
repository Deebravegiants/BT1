# [H] ALPINE-CVE-2016-7945

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7945
Ecosystem: Alpine:v3.2
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7945
Type: osv

## Affected
- Alpine:v3.2: `libxi` — affected >=0 <1.7.4-r1

## Details
Multiple integer overflows in X.org libXi before 1.7.7 allow remote X servers to cause a denial of service (out-of-bounds memory access or infinite loop) via vectors involving length fields.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7945
