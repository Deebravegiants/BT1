# [H] CVE-2020-11579

## Summary
Severity: High
Advisory: CVE-2020-11579
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/CVE-2020-11579
Type: osv

## Details
An issue was discovered in Chadha PHPKB 9.0 Enterprise Edition. installer/test-connection.php (part of the installation process) allows a remote unauthenticated attacker to disclose local files on hosts running PHP before 7.2.16, or on hosts where the MySQL ALLOW LOCAL DATA INFILE option is enabled.

## References
- https://www.phpkb.com
- https://shielder.it/
- https://github.com/ShielderSec/CVE-2020-11579
- https://www.shielder.it/blog/mysql-and-cve-2020-11579-exploitation/
