# [H] ALPINE-CVE-2019-18390

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18390
Ecosystem: Alpine:v3.11
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18390
Type: osv

## Affected
- Alpine:v3.11: `virglrenderer` — affected >=0 <0.8.1-r0

## Details
An out-of-bounds read in the vrend_blit_need_swizzle function in vrend_renderer.c in virglrenderer through 0.8.0 allows guest OS users to cause a denial of service via VIRGL_CCMD_BLIT commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18390
