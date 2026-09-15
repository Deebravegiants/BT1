# [M] ALPINE-CVE-2018-3838

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-3838
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-3838
Type: osv

## Affected
- Alpine:v3.5: `sdl2_image` — affected >=0 <2.0.1-r2
- Alpine:v3.6: `sdl2_image` — affected >=0 <2.0.1-r2
- Alpine:v3.7: `sdl2_image` — affected >=0 <2.0.2-r1

## Details
An exploitable information vulnerability exists in the XCF image rendering functionality of Simple DirectMedia Layer SDL2_image-2.0.2. A specially crafted XCF image can cause an out-of-bounds read on the heap, resulting in information disclosure. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-3838
