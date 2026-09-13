# [M] CVE-2020-35530

## Summary
Severity: Medium
Advisory: CVE-2020-35530
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-35530
Type: osv

## Details
In LibRaw, there is an out-of-bounds write vulnerability within the "new_node()" function (libraw\src\x3f\x3f_utils_patched.cpp) that can be triggered via a crafted X3F file.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00024.html
- https://github.com/LibRaw/LibRaw/commit/11c4db253ef2c9bb44247b578f5caa57c66a1eeb
- https://github.com/LibRaw/LibRaw/issues/272
