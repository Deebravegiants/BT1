# [M] CVE-2022-42325

## Summary
Severity: Medium
Advisory: CVE-2022-42325
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42325
Type: osv

## Details
Xenstore: Guests can create arbitrary number of nodes via transactions T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] In case a node has been created in a transaction and it is later deleted in the same transaction, the transaction will be terminated with an error. As this error is encountered only when handling the deleted node at transaction finalization, the transaction will have been performed partially and without updating the accounting information. This will enable a malicious guest to create arbitrary number of nodes.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/11/01/11
- http://xenbits.xen.org/xsa/advisory-421.html
- https://xenbits.xenproject.org/xsa/advisory-421.txt
