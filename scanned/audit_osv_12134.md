# [H] CVE-2018-10529

## Summary
Severity: High
Advisory: CVE-2018-10529
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10529
Type: osv

## Details
An issue was discovered in LibRaw 0.18.9. There is an out-of-bounds read affecting the X3F property table list implementation in libraw_x3f.cpp and libraw_cxx.cpp.

## References
- https://github.com/LibRaw/LibRaw/issues/144
- https://usn.ubuntu.com/3639-1/
- https://github.com/LibRaw/LibRaw/commit/f0c505a3e5d47989a5f69be2d0d4f250af6b1a6c
