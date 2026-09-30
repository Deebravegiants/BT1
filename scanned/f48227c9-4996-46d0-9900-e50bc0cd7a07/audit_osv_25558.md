# [C] Unauthenticated SQL Injection in graph_view.php in Cacti

## Summary
Severity: Critical
Advisory: CVE-2023-39361
Aliases: GHSA-6r43-q2fw-5wrg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-39361
Type: osv

## Details
Cacti is an open source operational monitoring and fault management framework. Affected versions are subject to a SQL injection discovered in graph_view.php. Since guest users can access graph_view.php without authentication by default, if guest users are being utilized in an enabled state, there could be the potential for significant damage. Attackers may exploit this vulnerability, and there may be possibilities for actions such as the usurpation of administrative privileges or remote code execution. This issue has been addressed in version 1.2.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFH3J2WVBKY4ZJNMARVOWJQK6PSLPHFH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOQFYGLZBAWT4AWNMO7DU73QXWPXTCKH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZGB2UXJEUYWWA6IWVFQ3ZTP22FIHMGN/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39361.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-6r43-q2fw-5wrg
- https://nvd.nist.gov/vuln/detail/CVE-2023-39361
- https://www.debian.org/security/2023/dsa-5550
