# [M] CVE-2025-49641

## Summary
Severity: Medium
Advisory: CVE-2025-49641
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-49641
Type: osv

## Details
A regular Zabbix user with no permission to the Monitoring -> Problems view is still able to call the problem.view.refresh action and therefore still retrieve a list of active problems.

## References
- https://support.zabbix.com/browse/ZBX-27063
