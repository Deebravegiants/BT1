# [H] CVE-2024-33655

## Summary
Severity: High
Advisory: CVE-2024-33655
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-33655
Type: osv

## Details
The DNS protocol in RFC 1035 and updates allows remote attackers to cause a denial of service (resource consumption) by arranging for DNS queries to be accumulated for seconds, such that responses are later sent in a pulsing burst (which can be considered traffic amplification in some cases), aka the "DNSBomb" issue.

## References
- https://alas.aws.amazon.com/ALAS-2024-1934.html
- https://datatracker.ietf.org/doc/html/rfc1035
- https://github.com/TechnitiumSoftware/DnsServer/blob/master/CHANGELOG.md#version-120
- https://lists.debian.org/debian-lts-announce/2025/08/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3TBXPRJ2Q235YUZKYDRWOSYNDFBJQWJ3/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QITY2QBX2OCBTZIXD2A5ES62STFIA4AL/
- https://meterpreter.org/researchers-uncover-dnsbomb-a-new-pdos-attack-exploiting-legitimate-dns-features/
- https://nlnetlabs.nl/downloads/unbound/CVE-2024-33655.txt
- https://sp2024.ieee-security.org/accepted-papers.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33655.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3TBXPRJ2Q235YUZKYDRWOSYNDFBJQWJ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QITY2QBX2OCBTZIXD2A5ES62STFIA4AL/
- https://nlnetlabs.nl/projects/unbound/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2024-33655
- https://gitlab.isc.org/isc-projects/bind9/-/issues/4398
- https://github.com/NLnetLabs/unbound/commit/c3206f4568f60c486be6d165b1f2b5b254fea3de
- https://www.isc.org/blogs/2024-dnsbomb/
