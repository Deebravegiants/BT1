# [H] ALPINE-CVE-2016-3172

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-3172
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3172
Type: osv

## Affected
- Alpine:v3.2: `cacti` — affected >=0 <0.8.8g-r1
- Alpine:v3.3: `cacti` — affected >=0 <0.8.8g-r1

## Details
SQL injection vulnerability in tree.php in Cacti 0.8.8g and earlier allows remote authenticated users to execute arbitrary SQL commands via the parent_id parameter in an item_edit action.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3172
