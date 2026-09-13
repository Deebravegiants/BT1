# [C] CVE-2021-31870

## Summary
Severity: Critical
Advisory: CVE-2021-31870
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-31870
Type: osv

## Details
An issue was discovered in klibc before 2.0.9. Multiplication in the calloc() function may result in an integer overflow and a subsequent heap buffer overflow.

## References
- https://kernel.org/pub/linux/libs/klibc/2.0/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00025.html
- https://lists.zytor.com/archives/klibc/2021-April/004593.html
- http://www.openwall.com/lists/oss-security/2021/04/30/1
- https://git.kernel.org/pub/scm/libs/klibc/klibc.git/commit/?id=292650f04c2b5348b4efbad61fb014ed09b4f3f2
