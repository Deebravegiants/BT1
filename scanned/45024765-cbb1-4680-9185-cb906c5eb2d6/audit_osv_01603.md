# [H] ALPINE-CVE-2019-5059

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-5059
Ecosystem: Alpine:v3.10, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5059
Type: osv

## Affected
- Alpine:v3.10: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.7: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.8: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.9: `sdl2_image` — affected >=0 <2.0.5-r0

## Details
An exploitable code execution vulnerability exists in the XPM image rendering functionality of SDL2_image 2.0.4. A specially crafted XPM image can cause an integer overflow, allocating too small of a buffer. This buffer can then be written out of bounds resulting in a heap overflow, ultimately ending in code execution. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5059
