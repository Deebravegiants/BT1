# [H] CVE-2019-19647

## Summary
Severity: High
Advisory: CVE-2019-19647
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2019-19647
Type: osv

## Details
radare2 through 4.0.0 lacks validation of the content variable in the function r_asm_pseudo_incbin at libr/asm/asm.c, ultimately leading to an arbitrary write. This allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via crafted input.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WRQXCOVFWZIIMAZIAAFAVQGZOS7LGHXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YQTOWEDFXDTGTD6D4NHRB4FUURQSTTEN/
- https://github.com/radareorg/radare2/issues/15545
