# [M] Opensc: potential pin bypass when card tracks its own login state

## Summary
Severity: Medium
Advisory: CVE-2023-40660
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-40660
Type: osv

## Details
A flaw was found in OpenSC packages that allow a potential PIN bypass. When a token/card is authenticated by one process, it can perform cryptographic operations in other processes when an empty zero-length pin is passed. This issue poses a security risk, particularly for OS logon/screen unlock and for small, permanently connected tokens to computers. Additionally, the token can internally track login status. This flaw allows an attacker to gain unauthorized access, carry out malicious actions, or compromise the system without the user's awareness.

## References
- http://www.openwall.com/lists/oss-security/2023/12/13/2
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/OpenSC/OpenSC/releases/tag/0.24.0-rc1
- https://lists.debian.org/debian-lts-announce/2023/11/msg00024.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3CPQOMCDWFRBMEFR5VK4N5MMXXU42ODE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GLYEFIBBA37TK3UNMZN5NOJ7IWCIXLQP/
- https://access.redhat.com/errata/RHSA-2023:7876
- https://access.redhat.com/errata/RHSA-2023:7879
- https://access.redhat.com/security/cve/CVE-2023-40660
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40660.json
- https://github.com/OpenSC/OpenSC/wiki/OpenSC-security-advisories
- https://nvd.nist.gov/vuln/detail/CVE-2023-40660
- https://bugzilla.redhat.com/show_bug.cgi?id=2240912
- https://github.com/OpenSC/OpenSC/issues/2792#issuecomment-1674806651
- https://github.com/OpenSC/OpenSC
