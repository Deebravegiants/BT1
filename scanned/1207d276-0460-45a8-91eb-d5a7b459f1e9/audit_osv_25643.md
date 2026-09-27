# [M] Opensc: multiple memory issues with pkcs15-init (enrollment tool)

## Summary
Severity: Medium
Advisory: CVE-2023-40661
CVSS: 5.4 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-40661
Type: osv

## Details
Several memory vulnerabilities were identified within the OpenSC packages, particularly in the card enrollment process using pkcs15-init when a user or administrator enrolls cards. To take advantage of these flaws, an attacker must have physical access to the computer system and employ a custom-crafted USB device or smart card to manipulate responses to APDUs. This manipulation can potentially allow 
compromise key generation, certificate loading, and other card management operations during enrollment.

## References
- http://www.openwall.com/lists/oss-security/2023/12/13/3
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/OpenSC/OpenSC/releases/tag/0.24.0-rc1
- https://lists.debian.org/debian-lts-announce/2023/11/msg00024.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3CPQOMCDWFRBMEFR5VK4N5MMXXU42ODE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GLYEFIBBA37TK3UNMZN5NOJ7IWCIXLQP/
- https://access.redhat.com/errata/RHSA-2023:7876
- https://access.redhat.com/errata/RHSA-2023:7879
- https://access.redhat.com/security/cve/CVE-2023-40661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40661.json
- https://github.com/OpenSC/OpenSC/wiki/OpenSC-security-advisories
- https://nvd.nist.gov/vuln/detail/CVE-2023-40661
- https://bugzilla.redhat.com/show_bug.cgi?id=2240913
- https://github.com/OpenSC/OpenSC/issues/2792#issuecomment-1674806651
- https://github.com/OpenSC/OpenSC
