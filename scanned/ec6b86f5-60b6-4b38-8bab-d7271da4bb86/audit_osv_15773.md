# [H] CVE-2019-19590

## Summary
Severity: High
Advisory: CVE-2019-19590
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-05
Source: https://osv.dev/vulnerability/CVE-2019-19590
Type: osv

## Details
In radare2 through 4.0, there is an integer overflow for the variable new_token_size in the function r_asm_massemble at libr/asm/asm.c. This integer overflow will result in a Use-After-Free for the buffer tokens, which can be filled with arbitrary malicious data after the free. This allows remote attackers to cause a denial of service (application crash) or possibly execute arbitrary code via crafted input.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WRQXCOVFWZIIMAZIAAFAVQGZOS7LGHXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YQTOWEDFXDTGTD6D4NHRB4FUURQSTTEN/
- https://github.com/radareorg/radare2/issues/15543
