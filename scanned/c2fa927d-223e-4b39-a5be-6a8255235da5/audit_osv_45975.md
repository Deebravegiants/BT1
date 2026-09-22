# [M] JLSEC-2026-534

## Summary
Severity: Medium
Advisory: JLSEC-2026-534
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-534
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.4.0+0

## Details
`jp2/opj_decompress.c` in OpenJPEG through 2.3.1 has a use-after-free that can be triggered if there is a mix of valid and invalid files in a directory operated on by the decompressor. Triggering a double-free may also be possible. This is related to calling `opj_image_destroy` twice.

## References
- https://github.com/uclouvain/openjpeg/issues/1261
- https://lists.debian.org/debian-lts-announce/2020/07/msg00008.html
- https://pastebin.com/4sDKQ7U8
- https://security.gentoo.org/glsa/202101-29
- https://www.debian.org/security/2021/dsa-4882
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
