# [H] ALPINE-CVE-2022-44638

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-44638
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-44638
Type: osv

## Affected
- Alpine:v3.13: `pixman` — affected >=0 <0.40.0-r3
- Alpine:v3.14: `pixman` — affected >=0 <0.40.0-r3
- Alpine:v3.15: `pixman` — affected >=0 <0.40.0-r4
- Alpine:v3.16: `pixman` — affected >=0 <0.40.0-r4

## Details
In libpixman in Pixman before 0.42.2, there is an out-of-bounds write (aka heap-based buffer overflow) in rasterize_edges_8 due to an integer overflow in pixman_sample_floor_y.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-44638
