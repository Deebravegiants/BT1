# [H] Authenticated command injection in SNMP options of a Device

## Summary
Severity: High
Advisory: CVE-2023-39362
Aliases: GHSA-g6ff-58cj-x3cp
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-39362
Type: osv

## Details
Cacti is an open source operational monitoring and fault management framework. In Cacti 1.2.24, under certain conditions, an authenticated privileged user, can use a malicious string in the SNMP options of a Device, performing command injection and obtaining remote code execution on the underlying server. The `lib/snmp.php` file has a set of functions, with similar behavior, that accept in input some variables and place them into an `exec` call without a proper escape or validation. This issue has been addressed in version 1.2.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- http://packetstormsecurity.com/files/175029/Cacti-1.2.24-Command-Injection.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFH3J2WVBKY4ZJNMARVOWJQK6PSLPHFH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOQFYGLZBAWT4AWNMO7DU73QXWPXTCKH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZGB2UXJEUYWWA6IWVFQ3ZTP22FIHMGN/
- https://www.vicarius.io/vsociety/posts/command-injection-in-cacti-cve-2023-39362
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39362.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-g6ff-58cj-x3cp
- https://nvd.nist.gov/vuln/detail/CVE-2023-39362
- https://www.debian.org/security/2023/dsa-5550
