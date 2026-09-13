# [H] SQL Injection vulnerability in automation_get_new_graphs_sql

## Summary
Severity: High
Advisory: CVE-2024-31445
Aliases: GHSA-vjph-r677-6pcc
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-31445
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. Prior to version 1.2.27, a SQL injection vulnerability in `automation_get_new_graphs_sql` function of `api_automation.php` allows authenticated users to exploit these SQL injection vulnerabilities to perform privilege escalation and remote code execution. In `api_automation.php` line 856, the `get_request_var('filter')` is being concatenated into the SQL statement without any sanitization. In `api_automation.php` line 717, The filter of `'filter'` is `FILTER_DEFAULT`, which means there is no filter for it. Version 1.2.27 contains a patch for the issue.

## References
- https://github.com/Cacti/cacti/blob/501712998589763d411a68d35e3cda98fd9cfd18/lib/api_automation.php#L717
- https://github.com/Cacti/cacti/blob/501712998589763d411a68d35e3cda98fd9cfd18/lib/api_automation.php#L856
- https://lists.debian.org/debian-lts-announce/2024/09/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31445.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-vjph-r677-6pcc
- https://nvd.nist.gov/vuln/detail/CVE-2024-31445
- https://github.com/Cacti/cacti/commit/fd93c6e47651958b77c3bbe6a01fff695f81e886
