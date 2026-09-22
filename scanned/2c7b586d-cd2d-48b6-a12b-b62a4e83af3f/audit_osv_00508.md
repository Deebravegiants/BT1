# [H] ALPINE-CVE-2017-14448

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14448
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14448
Type: osv

## Affected
- Alpine:v3.10: `sdl2_image` — affected >=0 <2.0.3-r0
- Alpine:v3.11: `sdl2_image` — affected >=0 <2.0.3-r0
- Alpine:v3.5: `sdl2_image` — affected >=0 <2.0.1-r2
- Alpine:v3.6: `sdl2_image` — affected >=0 <2.0.1-r2
- Alpine:v3.7: `sdl2_image` — affected >=0 <2.0.2-r1
- Alpine:v3.8: `sdl2_image` — affected >=0 <2.0.3-r0
- Alpine:v3.9: `sdl2_image` — affected >=0 <2.0.3-r0

## Details
An exploitable code execution vulnerability exists in the XCF image rendering functionality of SDL2_image-2.0.2. A specially crafted XCF image can cause a heap overflow resulting in code execution. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14448
