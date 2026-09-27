# [C] CVE-2023-32728

## Summary
Severity: Critical
Advisory: CVE-2023-32728
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-32728
Type: osv

## Details
The Zabbix Agent 2 item key smart.disk.get does not sanitize its parameters before passing them to a shell command resulting possible vulnerability for remote code execution.

## References
- https://support.zabbix.com/browse/ZBX-23858
