# [M] CVE-2019-16903

## Summary
Severity: Medium
Advisory: CVE-2019-16903
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2019-16903
Type: osv

## Details
Platinum UPnP SDK 1.2.0 allows Directory Traversal in Core/PltHttpServer.cpp because it checks for /.. where it should be checking for ../ instead.

## References
- https://github.com/plutinosoft/Platinum/issues/22
- http://www.iwantacve.cn/index.php/archives/349/
