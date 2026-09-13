# [H] CVE-2022-42327

## Summary
Severity: High
Advisory: CVE-2022-42327
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42327
Type: osv

## Details
x86: unintended memory sharing between guests On Intel systems that support the "virtualize APIC accesses" feature, a guest can read and write the global shared xAPIC page by moving the local APIC out of xAPIC mode. Access to this shared page bypasses the expected isolation that should exist between two guests.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://security.gentoo.org/glsa/202402-07
- https://xenbits.xenproject.org/xsa/advisory-412.txt
- http://www.openwall.com/lists/oss-security/2022/11/01/3
- http://xenbits.xen.org/xsa/advisory-412.html
