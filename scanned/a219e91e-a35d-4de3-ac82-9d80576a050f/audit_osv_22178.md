# [M] CVE-2022-23134

## Summary
Severity: Medium
Advisory: CVE-2022-23134
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2022-23134
Type: osv

## Details
After the initial setup process, some steps of setup.php file are reachable not only by super-administrators, but by unauthenticated users as well. Malicious actor can pass step checks and potentially change the configuration of Zabbix Frontend.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-23134
- https://lists.debian.org/debian-lts-announce/2022/02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6SZYHXINBKCY42ITFSNCYE7KCSF33VRA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VB6W556GVXOKUYTASTDGL3AI7S3SJHX7/
- https://support.zabbix.com/browse/ZBX-20384
