# [M] Opensc: out-of-bounds read in myeid driver handling encryption using symmetric keys

## Summary
Severity: Medium
Advisory: CVE-2023-4535
CVSS: 4.5 (CVSS:3.1/AV:P/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-4535
Type: osv

## Details
An out-of-bounds read vulnerability was found in OpenSC packages within the MyEID driver when handling symmetric key encryption. Exploiting this flaw requires an attacker to have physical access to the computer and a specially crafted USB device or smart card. This flaw allows the attacker to manipulate APDU responses and potentially gain unauthorized access to sensitive data, compromising the system's security.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/OpenSC/OpenSC/releases/tag/0.24.0-rc1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3CPQOMCDWFRBMEFR5VK4N5MMXXU42ODE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GLYEFIBBA37TK3UNMZN5NOJ7IWCIXLQP/
- https://access.redhat.com/errata/RHSA-2023:7879
- https://access.redhat.com/security/cve/CVE-2023-4535
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4535.json
- https://github.com/OpenSC/OpenSC/wiki/OpenSC-security-advisories
- https://nvd.nist.gov/vuln/detail/CVE-2023-4535
- https://bugzilla.redhat.com/show_bug.cgi?id=2240914
- https://github.com/OpenSC/OpenSC/issues/2792#issuecomment-1674806651
- https://github.com/OpenSC/OpenSC/commit/f1993dc4e0b33050b8f72a3558ee88b24c4063b2
