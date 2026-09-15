# [C] CVE-2021-31873

## Summary
Severity: Critical
Advisory: CVE-2021-31873
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-31873
Type: osv

## Details
An issue was discovered in klibc before 2.0.9. Additions in the malloc() function may result in an integer overflow and a subsequent heap buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2021/04/30/1
- https://kernel.org/pub/linux/libs/klibc/2.0/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00025.html
- https://lists.zytor.com/archives/klibc/2021-April/004593.html
- https://git.kernel.org/pub/scm/libs/klibc/klibc.git/commit/?id=a31ae8c508fc8d1bca4f57e9f9f88127572d5202
- https://github.com/huolinjue/klibc/commit/a31ae8c508fc8d1bca4f57e9f9f88127572d5202
