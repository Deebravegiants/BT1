# [H] CVE-2018-14338

## Summary
Severity: High
Advisory: CVE-2018-14338
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14338
Type: osv

## Details
samples/geotag.cpp in the example code of Exiv2 0.26 misuses the realpath function on POSIX platforms (other than Apple platforms) where glibc is not used, possibly leading to a buffer overflow.

## References
- https://github.com/Exiv2/exiv2/issues/382
