# [M] CVE-2022-42321

## Summary
Severity: Medium
Advisory: CVE-2022-42321
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42321
Type: osv

## Details
Xenstore: Guests can crash xenstored via exhausting the stack Xenstored is using recursion for some Xenstore operations (e.g. for deleting a sub-tree of Xenstore nodes). With sufficiently deep nesting levels this can result in stack exhaustion on xenstored, leading to a crash of xenstored.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/11/01/8
- https://xenbits.xenproject.org/xsa/advisory-418.txt
- http://xenbits.xen.org/xsa/advisory-418.html
