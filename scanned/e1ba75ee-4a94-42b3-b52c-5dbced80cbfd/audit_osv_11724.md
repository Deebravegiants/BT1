# [H] CVE-2017-9427

## Summary
Severity: High
Advisory: CVE-2017-9427
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-04
Source: https://osv.dev/vulnerability/CVE-2017-9427
Type: osv

## Details
SQL injection vulnerability in BigTree CMS through 4.2.18 allows remote authenticated users to execute arbitrary SQL commands via core\admin\modules\developer\modules\designer\form-create.php. The attacker creates a crafted table name at admin/developer/modules/designer/ and the injection is visible at admin/dashboard/vitals-statistics/integrity/check/?external=true.

## References
- https://github.com/bigtreecms/BigTree-CMS/issues/288
