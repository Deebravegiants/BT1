# [M] CVE-2022-42331

## Summary
Severity: Medium
Advisory: CVE-2022-42331
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-21
Source: https://osv.dev/vulnerability/CVE-2022-42331
Type: osv

## Details
x86: speculative vulnerability in 32bit SYSCALL path Due to an oversight in the very original Spectre/Meltdown security work (XSA-254), one entrypath performs its speculation-safety actions too late. In some configurations, there is an unprotected RET instruction which can be attacked with a variety of speculative attacks.

## References
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2023/dsa-5378
- https://xenbits.xenproject.org/xsa/advisory-429.txt
- http://www.openwall.com/lists/oss-security/2023/03/21/3
- http://xenbits.xen.org/xsa/advisory-429.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5L6PM4RE7MUE6OWA32ZVOXCP235RM2TM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/APBMS2Q6746AXAFAITNJMGBNFGNMVLWR/
