# [H] CVE-2020-12244

## Summary
Severity: High
Advisory: CVE-2020-12244
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-12244
Type: osv

## Details
An issue has been found in PowerDNS Recursor 4.1.0 through 4.3.0 where records in the answer section of a NXDOMAIN response lacking an SOA were not properly validated in SyncRes::processAnswer, allowing an attacker to bypass DNSSEC validation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NMP72NJGKBWR5WEBXAWX5KSLQUDFTG6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PS4ZN5XGENYNFKX7QIIOUCQQHXE37GJF/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00052.html
- http://www.openwall.com/lists/oss-security/2020/05/19/3
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2020-02.html
- https://www.debian.org/security/2020/dsa-4691
