# [C] CVE-2021-31872

## Summary
Severity: Critical
Advisory: CVE-2021-31872
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-31872
Type: osv

## Details
An issue was discovered in klibc before 2.0.9. Multiple possible integer overflows in the cpio command on 32-bit systems may result in a buffer overflow or other security impact.

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00025.html
- https://lists.zytor.com/archives/klibc/2021-April/004593.html
- http://www.openwall.com/lists/oss-security/2021/04/30/1
- https://kernel.org/pub/linux/libs/klibc/2.0/
- https://git.kernel.org/pub/scm/libs/klibc/klibc.git/commit/?id=9b1c91577aef7f2e72c3aa11a27749160bd278ff
