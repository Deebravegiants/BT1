# [H] CVE-2018-17418

## Summary
Severity: High
Advisory: CVE-2018-17418
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2018-17418
Type: osv

## Details
Monstra CMS 3.0.4 allows remote attackers to execute arbitrary PHP code via a mixed-case file extension, as demonstrated by the 123.PhP filename, because plugins\box\filesmanager\filesmanager.admin.php mishandles the forbidden_types variable.

## References
- https://github.com/AlwaysHereFight/monstra_cms-3.0.4--getshell/blob/master/README.md
