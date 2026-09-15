# [H] CVE-2019-11222

## Summary
Severity: High
Advisory: CVE-2019-11222
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-15
Source: https://osv.dev/vulnerability/CVE-2019-11222
Type: osv

## Details
gf_bin128_parse in utils/os_divers.c in GPAC 0.7.1 has a buffer overflow issue for the crypt feature when encountering a crafted_drm_file.xml file.

## References
- https://lists.debian.org/debian-lts-announce/2019/04/msg00025.html
- https://github.com/gpac/gpac/issues/1204
- https://github.com/gpac/gpac/issues/1205
- https://github.com/gpac/gpac/commit/f3698bb1bce62402805c3fda96551a23101a32f9
