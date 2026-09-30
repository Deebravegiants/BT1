# [H] CVE-2021-32494

## Summary
Severity: High
Advisory: CVE-2021-32494
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-07
Source: https://osv.dev/vulnerability/CVE-2021-32494
Type: osv

## Details
Radare2 has a division by zero vulnerability in Mach-O parser's rebase_buffer function. This allow attackers to create malicious inputs that can cause denial of service.

## References
- https://github.com/radareorg/radare2/commit/a07dedb804a82bc01c07072861942dd80c6b6d62
- https://github.com/radareorg/radare2/issues/18667
