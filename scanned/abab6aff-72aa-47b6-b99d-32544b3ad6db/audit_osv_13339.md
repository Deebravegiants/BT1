# [H] CVE-2018-19395

## Summary
Severity: High
Advisory: CVE-2018-19395
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-20
Source: https://osv.dev/vulnerability/CVE-2018-19395
Type: osv

## Details
ext/standard/var.c in PHP 5.x through 7.1.24 on Windows allows attackers to cause a denial of service (NULL pointer dereference and application crash) because com and com_safearray_proxy return NULL in com_properties_get in ext/com_dotnet/com_handlers.c, as demonstrated by a serialize call on COM("WScript.Shell").

## References
- http://www.securityfocus.com/bid/105989
- https://security.netapp.com/advisory/ntap-20181221-0005/
- https://bugs.php.net/bug.php?id=77177
