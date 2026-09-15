# [C] ALPINE-CVE-2016-10134

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-10134
Ecosystem: Alpine:v3.5
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10134
Type: osv

## Affected
- Alpine:v3.5: `zabbix` — affected >=0 <3.0.4-r0

## Details
SQL injection vulnerability in Zabbix before 2.2.14 and 3.0 before 3.0.4 allows remote attackers to execute arbitrary SQL commands via the toggle_ids array parameter in latest.php.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10134
