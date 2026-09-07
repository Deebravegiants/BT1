# [C] codeigniter/framework SQL injection in ODBC database driver

## Summary
Severity: Critical
Advisory: GHSA-27qr-636m-wxg2
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-27qr-636m-wxg2
Type: github-advisory

## Affected
- Packagist: `codeigniter/framework` — affected >=0 <3.1.0

## Details
CodeIgniter 3.1.0 addressed a critical security issue within the ODBC database driver. This update includes crucial fixes to mitigate a SQL injection vulnerability, preventing potential exploitation by attackers. It is noteworthy that these fixes render the query builder and escape() functions incompatible with the ODBC driver. However, the update introduces actual query binding as a more secure alternative.

## References
- https://github.com/simplysites/CodeIgniter/commit/3d10ffa77854044570a1809a884776fd4bbd8b70
- https://forum.codeigniter.com/thread-65803.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter/framework/2016-07-26-1.yaml
- https://github.com/simplysites/CodeIgniter
