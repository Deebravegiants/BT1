# [H] CVE-2019-12482

## Summary
Severity: High
Advisory: CVE-2019-12482
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-30
Source: https://osv.dev/vulnerability/CVE-2019-12482
Type: osv

## Details
An issue was discovered in GPAC 0.7.1. There is a NULL pointer dereference in the function gf_isom_get_original_format_type at isomedia/drm_sample.c in libgpac.a, as demonstrated by MP4Box.

## References
- https://lists.debian.org/debian-lts-announce/2019/06/msg00030.html
- https://github.com/gpac/gpac/issues/1249
