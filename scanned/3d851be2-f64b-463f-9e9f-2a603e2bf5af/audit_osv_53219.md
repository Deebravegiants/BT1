# [M] CVE-2022-33748

## Summary
Severity: Medium
Advisory: CVE-2022-33748
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-33748
Type: osv

## Details
lock order inversion in transitive grant copy handling As part of XSA-226 a missing cleanup call was inserted on an error handling path. While doing so, locking requirements were not paid attention to. As a result two cooperating guests granting each other transitive grants can cause locks to be acquired nested within one another, but in respectively opposite order. With suitable timing between the involved grant copy operations this may result in the locking up of a CPU.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TJOMUNGW6VTK5CZZRLWLVVEOUPEQBRHI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWSC77GS5NATI3TT7FMVPULUPXR635XQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/10/11/2
- http://xenbits.xen.org/xsa/advisory-411.html
- https://xenbits.xenproject.org/xsa/advisory-411.txt
