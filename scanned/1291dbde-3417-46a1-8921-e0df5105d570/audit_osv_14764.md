# [C] CVE-2019-11344

## Summary
Severity: Critical
Advisory: CVE-2019-11344
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-19
Source: https://osv.dev/vulnerability/CVE-2019-11344
Type: osv

## Details
data/inc/files.php in Pluck 4.7.8 allows remote attackers to execute arbitrary code by uploading a .htaccess file that specifies SetHandler x-httpd-php for a .txt file, because only certain PHP-related filename extensions are blocked.

## References
- https://github.com/pluck-cms/pluck/issues/72
