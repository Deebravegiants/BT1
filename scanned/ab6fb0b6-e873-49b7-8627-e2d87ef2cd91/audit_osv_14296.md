# [M] CVE-2018-8808

## Summary
Severity: Medium
Advisory: CVE-2018-8808
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8808
Type: osv

## Details
In radare2 2.4.0, there is a heap-based buffer over-read in the r_asm_disassemble function of asm.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted dex file.

## References
- https://github.com/radare/radare2/issues/9725
