# [M] Unchecked regular expressions can lead to SQL Injection and data leakage in Cacti

## Summary
Severity: Medium
Advisory: CVE-2023-39365
Aliases: GHSA-v5w7-hww7-2f22
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:L)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-39365
Type: osv

## Details
Cacti is an open source operational monitoring and fault management framework. Issues with Cacti Regular Expression validation combined with the external links feature can lead to limited SQL Injections and subsequent data leakage. This issue has been addressed in version 1.2.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFH3J2WVBKY4ZJNMARVOWJQK6PSLPHFH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOQFYGLZBAWT4AWNMO7DU73QXWPXTCKH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZGB2UXJEUYWWA6IWVFQ3ZTP22FIHMGN/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39365.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-v5w7-hww7-2f22
- https://nvd.nist.gov/vuln/detail/CVE-2023-39365
- https://www.debian.org/security/2023/dsa-5550
