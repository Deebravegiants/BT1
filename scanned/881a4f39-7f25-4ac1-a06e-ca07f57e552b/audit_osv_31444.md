# [C] Asterisk Unsafe Shell Sourcing in safe_asterisk Leads to Local Privilege Escalation

## Summary
Severity: Critical
Advisory: CVE-2025-1131
Aliases: GHSA-v9q8-9j8m-5xwp
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N/V:C/RE:H/U:Amber)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-1131
Type: osv

## Details
A local privilege escalation vulnerability exists in the safe_asterisk script included with the Asterisk toolkit package. When Asterisk is started via this script (common in SysV init or FreePBX environments), it sources all .sh files located in /etc/asterisk/startup.d/ as root, without validating ownership or permissions.


Non-root users with legitimate write access to /etc/asterisk can exploit this behaviour by placing malicious scripts in the startup.d directory, which will then execute with root privileges upon service restart.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00006.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1131.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-v9q8-9j8m-5xwp
- https://nvd.nist.gov/vuln/detail/CVE-2025-1131
- https://github.com/asterisk/asterisk
