# [M] CVE-2018-20456

## Summary
Severity: Medium
Advisory: CVE-2018-20456
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20456
Type: osv

## Details
In radare2 prior to 3.1.1, the parseOperand function inside libr/asm/p/asm_x86_nz.c may allow attackers to cause a denial of service (application crash in libr/util/strbuf.c via a stack-based buffer over-read) by crafting an input file, a related issue to CVE-2018-20455.

## References
- https://github.com/radare/radare2/commit/9b46d38dd3c4de6048a488b655c7319f845af185
- https://github.com/radare/radare2/issues/12372
