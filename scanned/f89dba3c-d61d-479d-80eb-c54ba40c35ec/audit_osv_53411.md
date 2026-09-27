# [M] CVE-2022-42310

## Summary
Severity: Medium
Advisory: CVE-2022-42310
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42310
Type: osv

## Details
Xenstore: Guests can create orphaned Xenstore nodes By creating multiple nodes inside a transaction resulting in an error, a malicious guest can create orphaned nodes in the Xenstore data base, as the cleanup after the error will not remove all nodes already created. When the transaction is committed after this situation, nodes without a valid parent can be made permanent in the data base.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- https://xenbits.xenproject.org/xsa/advisory-415.txt
- http://www.openwall.com/lists/oss-security/2022/11/01/5
- http://xenbits.xen.org/xsa/advisory-415.html
