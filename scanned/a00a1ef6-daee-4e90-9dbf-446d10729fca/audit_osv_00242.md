# [C] ALPINE-CVE-2016-7947

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7947
Ecosystem: Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7947
Type: osv

## Affected
- Alpine:v3.3: `libxrandr` — affected >=0 <1.5.0-r1

## Details
Multiple integer overflows in X.org libXrandr before 1.5.1 allow remote X servers to trigger out-of-bounds write operations via a crafted response.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7947
