# [M] CVE-2017-12419

## Summary
Severity: Medium
Advisory: CVE-2017-12419
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-05
Source: https://osv.dev/vulnerability/CVE-2017-12419
Type: osv

## Details
If, after successful installation of MantisBT through 2.5.2 on MySQL/MariaDB, the administrator does not remove the 'admin' directory (as recommended in the "Post-installation and upgrade tasks" section of the MantisBT Admin Guide), and the MySQL client has a local_infile setting enabled (in php.ini mysqli.allow_local_infile, or the MySQL client config file, depending on the PHP setup), an attacker may take advantage of MySQL's "connect file read" feature to remotely access files on the MantisBT server.

## References
- http://openwall.com/lists/oss-security/2017/08/04/6
- http://www.securityfocus.com/bid/100142
- https://mantisbt.org/bugs/view.php?id=23173
