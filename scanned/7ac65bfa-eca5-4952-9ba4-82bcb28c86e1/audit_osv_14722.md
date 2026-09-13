# [H] CVE-2019-11044

## Summary
Severity: High
Advisory: CVE-2019-11044
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-11044
Type: osv

## Details
In PHP versions 7.2.x below 7.2.26, 7.3.x below 7.3.13 and 7.4.0 on Windows, PHP link() function accepts filenames with embedded \0 byte and treats them as terminating at that byte. This could lead to security vulnerabilities, e.g. in applications checking paths that the code is allowed to access.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N7GCOAE6KVHYJ3UQ4KLPLTGSLX6IRVRN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWRQPYXVG43Q7DXMXH6UVWMKWGUW552F/
- https://security.netapp.com/advisory/ntap-20200103-0002/
- https://www.tenable.com/security/tns-2021-14
- https://bugs.php.net/bug.php?id=78862
