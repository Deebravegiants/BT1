# [M] CVE-2022-33746

## Summary
Severity: Medium
Advisory: CVE-2022-33746
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-33746
Type: osv

## Details
P2M pool freeing may take excessively long The P2M pool backing second level address translation for guests may be of significant size. Therefore its freeing may take more time than is reasonable without intermediate preemption checks. Such checking for the need to preempt was so far missing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TJOMUNGW6VTK5CZZRLWLVVEOUPEQBRHI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWSC77GS5NATI3TT7FMVPULUPXR635XQ/
- https://www.debian.org/security/2022/dsa-5272
- https://security.gentoo.org/glsa/202402-07
- http://www.openwall.com/lists/oss-security/2022/10/11/3
- http://xenbits.xen.org/xsa/advisory-410.html
- https://xenbits.xenproject.org/xsa/advisory-410.txt
