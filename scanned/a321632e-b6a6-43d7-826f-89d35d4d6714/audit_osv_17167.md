# [M] CVE-2020-13397

## Summary
Severity: Medium
Advisory: CVE-2020-13397
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-22
Source: https://osv.dev/vulnerability/CVE-2020-13397
Type: osv

## Details
An issue was discovered in FreeRDP before 2.1.1. An out-of-bounds (OOB) read vulnerability has been detected in security_fips_decrypt in libfreerdp/core/security.c due to an uninitialized value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/commit/8fb6336a4072abcee8ce5bd6ae91104628c7bb69
- https://github.com/FreeRDP/FreeRDP/compare/2.1.0...2.1.1
- https://lists.debian.org/debian-lts-announce/2020/08/msg00054.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4379-1/
- https://usn.ubuntu.com/4382-1/
- https://github.com/FreeRDP/FreeRDP/commit/d6cd14059b257318f176c0ba3ee0a348826a9ef8
