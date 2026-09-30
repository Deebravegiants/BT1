# [H] CVE-2020-13384

## Summary
Severity: High
Advisory: CVE-2020-13384
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-22
Source: https://osv.dev/vulnerability/CVE-2020-13384
Type: osv

## Details
Monstra CMS 3.0.4 allows remote authenticated users to upload and execute arbitrary PHP code via admin/index.php?id=filesmanager because, for example, .php filenames are blocked but .php7 filenames are not, a related issue to CVE-2017-18048.

## References
- https://www.exploit-db.com/exploits/48479
