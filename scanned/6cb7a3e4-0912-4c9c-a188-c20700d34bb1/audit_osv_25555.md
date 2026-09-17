# [H] A Defect in sql_save() Causes Multiple SQL Injection Vulnerabilities in Cacti

## Summary
Severity: High
Advisory: CVE-2023-39357
Aliases: GHSA-6jhp-mgqg-fhqg
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-39357
Type: osv

## Details
Cacti is an open source operational monitoring and fault management framework. A defect in the sql_save function was discovered. When the column type is numeric, the sql_save function directly utilizes user input. Many files and functions calling the sql_save function do not perform prior validation of user input, leading to the existence of multiple SQL injection vulnerabilities in Cacti. This allows authenticated users to exploit these SQL injection vulnerabilities to perform privilege escalation and remote code execution. This issue has been addressed in version 1.2.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFH3J2WVBKY4ZJNMARVOWJQK6PSLPHFH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOQFYGLZBAWT4AWNMO7DU73QXWPXTCKH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZGB2UXJEUYWWA6IWVFQ3ZTP22FIHMGN/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39357.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-6jhp-mgqg-fhqg
- https://nvd.nist.gov/vuln/detail/CVE-2023-39357
- https://www.debian.org/security/2023/dsa-5550
