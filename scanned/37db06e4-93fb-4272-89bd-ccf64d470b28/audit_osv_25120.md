# [H] Cacti Privilege Escalation

## Summary
Severity: High
Advisory: CVE-2023-31132
Aliases: GHSA-rf5w-pq3f-9876
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-31132
Type: osv

## Details
Cacti is an open source operational monitoring and fault management framework. Affected versions are subject to a privilege escalation vulnerability. A low-privileged OS user with access to a Windows host where Cacti is installed can create arbitrary PHP files in a web document directory. The user can then execute the PHP files under the security context of SYSTEM. This allows an attacker to escalate privilege from a normal user account to SYSTEM. This issue has been addressed in version 1.2.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFH3J2WVBKY4ZJNMARVOWJQK6PSLPHFH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOQFYGLZBAWT4AWNMO7DU73QXWPXTCKH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZGB2UXJEUYWWA6IWVFQ3ZTP22FIHMGN/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31132.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-rf5w-pq3f-9876
- https://nvd.nist.gov/vuln/detail/CVE-2023-31132
