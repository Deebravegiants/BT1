# [M] ALPINE-CVE-2017-7890

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7890
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7890
Type: osv

## Affected
- Alpine:v3.4: `gd` — affected >=0 <2.2.5-r0
- Alpine:v3.5: `gd` — affected >=0 <2.2.5-r0
- Alpine:v3.6: `gd` — affected >=0 <2.2.5-r0

## Details
The GIF decoding function gdImageCreateFromGifCtx in gd_gif_in.c in the GD Graphics Library (aka libgd), as used in PHP before 5.6.31 and 7.x before 7.1.7, does not zero colorMap arrays before use. A specially crafted GIF image could use the uninitialized tables to read ~700 bytes from the top of the stack, potentially disclosing sensitive information.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7890
