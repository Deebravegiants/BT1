# [H] CVE-2018-19396

## Summary
Severity: High
Advisory: CVE-2018-19396
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-20
Source: https://osv.dev/vulnerability/CVE-2018-19396
Type: osv

## Details
ext/standard/var_unserializer.c in PHP 5.x through 7.1.24 allows attackers to cause a denial of service (application crash) via an unserialize call for the com, dotnet, or variant class.

## References
- http://www.securityfocus.com/bid/105989
- https://security.netapp.com/advisory/ntap-20181221-0005/
- https://bugs.php.net/bug.php?id=77177
