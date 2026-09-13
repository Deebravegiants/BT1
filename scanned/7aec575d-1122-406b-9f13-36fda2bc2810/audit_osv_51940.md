# [H] CVE-2021-45911

## Summary
Severity: High
Advisory: CVE-2021-45911
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-28
Source: https://osv.dev/vulnerability/CVE-2021-45911
Type: osv

## Details
An issue was discovered in gif2apng 1.9. There is a heap-based buffer overflow in the main function. It allows an attacker to write 2 bytes outside the boundaries of the buffer.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00008.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1002687
