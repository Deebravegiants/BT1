# [M] CVE-2022-48619

## Summary
Severity: Medium
Advisory: CVE-2022-48619
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2022-48619
Type: osv

## Details
An issue was discovered in drivers/input/input.c in the Linux kernel before 5.17.10. An attacker can cause a denial of service (panic) because input_set_capability mishandles the situation in which an event code falls outside of a bitmap.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.10
- https://github.com/torvalds/linux/commit/409353cbe9fe48f6bc196114c442b1cff05a39bc
