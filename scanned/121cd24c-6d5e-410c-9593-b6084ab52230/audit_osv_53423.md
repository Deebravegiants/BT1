# [M] CVE-2022-42322

## Summary
Severity: Medium
Advisory: CVE-2022-42322
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42322
Type: osv

## Details
Xenstore: Cooperating guests can create arbitrary numbers of nodes T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Since the fix of XSA-322 any Xenstore node owned by a removed domain will be modified to be owned by Dom0. This will allow two malicious guests working together to create an arbitrary number of Xenstore nodes. This is possible by domain A letting domain B write into domain A's local Xenstore tree. Domain B can then create many nodes and reboot. The nodes created by domain B will now be owned by Dom0. By repeating this process over and over again an arbitrary number of nodes can be created, as Dom0's number of nodes isn't limited by Xenstore quota.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/11/01/9
- http://xenbits.xen.org/xsa/advisory-419.html
- https://xenbits.xenproject.org/xsa/advisory-419.txt
