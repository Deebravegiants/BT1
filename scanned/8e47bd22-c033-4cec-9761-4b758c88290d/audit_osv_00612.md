# [H] ALPINE-CVE-2017-2887

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-2887
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2887
Type: osv

## Affected
- Alpine:v3.5: `sdl2_image` — affected >=0 <2.0.1-r2
- Alpine:v3.6: `sdl2_image` — affected >=0 <2.0.1-r2

## Details
An exploitable buffer overflow vulnerability exists in the XCF property handling functionality of SDL_image 2.0.1. A specially crafted xcf file can cause a stack-based buffer overflow resulting in potential code execution. An attacker can provide a specially crafted XCF file to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2887
