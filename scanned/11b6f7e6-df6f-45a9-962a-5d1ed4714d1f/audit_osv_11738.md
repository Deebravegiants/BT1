# [H] CVE-2017-9449

## Summary
Severity: High
Advisory: CVE-2017-9449
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-06
Source: https://osv.dev/vulnerability/CVE-2017-9449
Type: osv

## Details
SQL injection vulnerability in BigTree CMS through 4.2.18 allows remote authenticated users to execute arbitrary SQL commands via core/admin/modules/developer/modules/views/create.php. The attacker creates a crafted table name at admin/developer/modules/views/create/ and the injection is visible at admin/ajax/auto-modules/views/searchable-page/ or admin/modules_name.

## References
- https://github.com/bigtreecms/BigTree-CMS/issues/295
