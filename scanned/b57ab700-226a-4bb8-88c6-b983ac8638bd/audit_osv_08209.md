# [C] CVE-2016-15031

## Summary
Severity: Critical
Advisory: CVE-2016-15031
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-06
Source: https://osv.dev/vulnerability/CVE-2016-15031
Type: osv

## Details
A vulnerability was found in PHP-Login 1.0. It has been declared as critical. This vulnerability affects the function checkLogin of the file login/scripts/class.loginscript.php of the component POST Parameter Handler. The manipulation of the argument myusername leads to sql injection. The attack can be initiated remotely. Upgrading to version 2.0 is able to address this issue. The patch is identified as 0083ec652786ddbb81335ea20da590df40035679. It is recommended to upgrade the affected component. VDB-228022 is the identifier assigned to this vulnerability.

## References
- https://github.com/ipoelnet/php-login/releases/tag/v2.0
- https://vuldb.com/?ctiid.228022
- https://vuldb.com/?id.228022
- https://github.com/ipoelnet/php-login/commit/0083ec652786ddbb81335ea20da590df40035679
