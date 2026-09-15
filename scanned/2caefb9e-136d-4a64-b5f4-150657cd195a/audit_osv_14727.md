# [C] CVE-2019-11049

## Summary
Severity: Critical
Advisory: CVE-2019-11049
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-11049
Type: osv

## Details
In PHP versions 7.3.x below 7.3.13 and 7.4.0 on Windows, when supplying custom headers to mail() function, due to mistake introduced in commit 78f4b4a2dcf92ddbccea1bb95f8390a18ac3342e, if the header is supplied in lowercase, this can result in double-freeing certain memory locations.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N7GCOAE6KVHYJ3UQ4KLPLTGSLX6IRVRN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWRQPYXVG43Q7DXMXH6UVWMKWGUW552F/
- https://seclists.org/bugtraq/2020/Feb/27
- https://security.netapp.com/advisory/ntap-20200103-0002/
- https://www.debian.org/security/2020/dsa-4626
- https://www.tenable.com/security/tns-2021-14
- https://bugs.php.net/bug.php?id=78943
