# [H] CVE-2020-13568

## Summary
Severity: High
Advisory: CVE-2020-13568
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-13
Source: https://osv.dev/vulnerability/CVE-2020-13568
Type: osv

## Details
SQL injection vulnerability exists in phpGACL 3.3.7. A specially crafted HTTP request can lead to a SQL injection. An attacker can send an HTTP request to trigger this vulnerability in admin/edit_group.php, when the POST parameter action is “Submit”, the POST parameter parent_id leads to a SQL injection.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1179
