# [M] JLSEC-2026-547

## Summary
Severity: Medium
Advisory: JLSEC-2026-547
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-547
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=2.4.0+0 <2.5.0+0

## Details
A flaw was found in the `opj2_decompress` program in openjpeg2 2.4.0 in the way it handles an input directory with a large number of files. When it fails to allocate a buffer to store the filenames of the input directory, it calls free() on an uninitialized pointer, leading to a segmentation fault and a denial of service.

## References
- https://github.com/uclouvain/openjpeg/issues/1368
- https://lists.debian.org/debian-lts-announce/2022/04/msg00006.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MIWSQFQWXDU4MT3XTVAO6HC7TVL3NHS7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RMKBAMK2CAM5TMC5TODKVCE5AAPTD5YV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ROSN5NRUFOH7HGLJ4ZSKPGAKLFXJALW4/
- https://security.gentoo.org/glsa/202209-04
