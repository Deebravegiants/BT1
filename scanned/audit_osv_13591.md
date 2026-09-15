# [M] CVE-2018-20460

## Summary
Severity: Medium
Advisory: CVE-2018-20460
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20460
Type: osv

## Details
In radare2 prior to 3.1.2, the parseOperands function in libr/asm/arch/arm/armass64.c allows attackers to cause a denial-of-service (application crash caused by stack-based buffer overflow) by crafting an input file.

## References
- https://github.com/radare/radare2/commit/df167c7db545953bb7f71c72e98e7a3ca0c793bf
- https://github.com/radare/radare2/issues/12376
