# [H] Remote code execution via Log Poisoning in Cacti

## Summary
Severity: High
Advisory: CVE-2024-43363
Aliases: GHSA-gxq4-mv8h-6qj4
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-07
Source: https://osv.dev/vulnerability/CVE-2024-43363
Type: osv

## Details
Cacti is an open source performance and fault management framework. An admin user can create a device with a malicious hostname containing php code and repeat the installation process (completing only step 5 of the installation process is enough, no need to complete the steps before or after it) to use a php file as the cacti log file. After having the malicious hostname end up in the logs (log poisoning), one can simply go to the log file url to execute commands to achieve RCE. This issue has been addressed in version 1.2.28 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43363.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-gxq4-mv8h-6qj4
- https://nvd.nist.gov/vuln/detail/CVE-2024-43363
