# [H] CVE-2021-31871

## Summary
Severity: High
Advisory: CVE-2021-31871
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-31871
Type: osv

## Details
An issue was discovered in klibc before 2.0.9. An integer overflow in the cpio command may result in a NULL pointer dereference on 64-bit systems.

## References
- https://kernel.org/pub/linux/libs/klibc/2.0/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00025.html
- https://lists.zytor.com/archives/klibc/2021-April/004593.html
- http://www.openwall.com/lists/oss-security/2021/04/30/1
- https://git.kernel.org/pub/scm/libs/klibc/klibc.git/commit/?id=2e48a12ab1e30d43498c2d53e878a11a1b5102d5
