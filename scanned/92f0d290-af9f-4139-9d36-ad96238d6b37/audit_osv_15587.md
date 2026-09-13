# [H] CVE-2019-17533

## Summary
Severity: High
Advisory: CVE-2019-17533
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2019-10-13
Source: https://osv.dev/vulnerability/CVE-2019-17533
Type: osv

## Details
Mat_VarReadNextInfo4 in mat4.c in MATIO 1.5.17 omits a certain '\0' character, leading to a heap-based buffer over-read in strdup_vprintf when uninitialized memory is accessed.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00037.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=16856
- https://github.com/tbeu/matio/commit/651a8e28099edb5fbb9e4e1d4d3238848f446c9a
