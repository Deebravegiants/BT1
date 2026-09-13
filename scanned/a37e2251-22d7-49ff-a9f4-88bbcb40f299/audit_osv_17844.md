# [M] CVE-2020-20739

## Summary
Severity: Medium
Advisory: CVE-2020-20739
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-11-20
Source: https://osv.dev/vulnerability/CVE-2020-20739
Type: osv

## Details
im_vips2dz in /libvips/libvips/deprecated/im_vips2dz.c in libvips before 8.8.2 has an uninitialized variable which may cause the leakage of remote server path or stack address.

## References
- https://lists.debian.org/debian-lts-announce/2020/11/msg00049.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZULVPQQ4QDFSQCXFYBUXEM7UXJAOKLSP/
- https://github.com/libvips/libvips/issues/1419
- https://github.com/libvips/libvips/commit/2ab5aa7bf515135c2b02d42e9a72e4c98e17031a
