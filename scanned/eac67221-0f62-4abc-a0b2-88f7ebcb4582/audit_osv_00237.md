# [C] ALPINE-CVE-2016-7942

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7942
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7942
Type: osv

## Affected
- Alpine:v3.2: `libx11` — affected >=0 <1.6.3-r1
- Alpine:v3.3: `libx11` — affected >=0 <1.6.3-r3

## Details
The XGetImage function in X.org libX11 before 1.6.4 might allow remote X servers to gain privileges via vectors involving image type and geometry, which triggers out-of-bounds read operations.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7942
