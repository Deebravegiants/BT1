# [H] CVE-2017-14152

## Summary
Severity: High
Advisory: CVE-2017-14152
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-14152
Type: osv

## Details
A mishandled zero case was discovered in opj_j2k_set_cinema_parameters in lib/openjp2/j2k.c in OpenJPEG 2.2.0. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service (heap-based buffer overflow affecting opj_write_bytes_LE in lib/openjp2/cio.c and opj_j2k_write_sot in lib/openjp2/j2k.c) or possibly remote code execution.

## References
- http://www.debian.org/security/2017/dsa-4013
- https://blogs.gentoo.org/ago/2017/08/16/openjpeg-heap-based-buffer-overflow-in-opj_write_bytes_le-cio-c/
- https://github.com/uclouvain/openjpeg/commit/4241ae6fbbf1de9658764a80944dc8108f2b4154
- https://github.com/uclouvain/openjpeg/issues/985
