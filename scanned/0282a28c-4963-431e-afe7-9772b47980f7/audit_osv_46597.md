# [H] CVE-2014-0236

## Summary
Severity: High
Advisory: CVE-2014-0236
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-16
Source: https://osv.dev/vulnerability/CVE-2014-0236
Type: osv

## Details
file before 5.18, as used in the Fileinfo component in PHP before 5.6.0, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a zero root_storage value in a CDF file, related to cdf.c and readcdf.c.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=f3f22ff5c697aef854ffc1918bce708b37481b0f
- http://php.net/ChangeLog-5.php
- https://bugs.php.net/bug.php?id=67329
