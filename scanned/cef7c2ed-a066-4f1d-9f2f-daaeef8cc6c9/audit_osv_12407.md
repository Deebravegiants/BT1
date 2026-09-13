# [C] CVE-2018-11736

## Summary
Severity: Critical
Advisory: CVE-2018-11736
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-11736
Type: osv

## Details
An issue was discovered in Pluck before 4.7.7-dev2. /data/inc/images.php allows remote attackers to upload and execute arbitrary PHP code by using the image/jpeg content type for a .htaccess file.

## References
- https://github.com/pluck-cms/pluck/releases/tag/4.7.7-dev2
- https://github.com/pluck-cms/pluck/issues/61
