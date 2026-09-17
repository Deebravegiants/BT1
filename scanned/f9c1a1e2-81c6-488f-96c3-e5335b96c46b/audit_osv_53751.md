# [M] CVE-2023-23039

## Summary
Severity: Medium
Advisory: CVE-2023-23039
CVSS: 5.7 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-02-22
Source: https://osv.dev/vulnerability/CVE-2023-23039
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.2.0-rc2. drivers/tty/vcc.c has a race condition and resultant use-after-free if a physically proximate attacker removes a VCC device while calling open(), aka a race condition between vcc_open() and vcc_remove().

## References
- https://lkml.org/lkml/2023/1/1/169
