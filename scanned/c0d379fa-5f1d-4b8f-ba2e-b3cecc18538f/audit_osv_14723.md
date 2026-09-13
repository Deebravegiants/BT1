# [M] CVE-2019-11045

## Summary
Severity: Medium
Advisory: CVE-2019-11045
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-11045
Type: osv

## Details
In PHP versions 7.2.x below 7.2.26, 7.3.x below 7.3.13 and 7.4.0, PHP DirectoryIterator class accepts filenames with embedded \0 byte and treats them as terminating at that byte. This could lead to security vulnerabilities, e.g. in applications checking paths that the code is allowed to access.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N7GCOAE6KVHYJ3UQ4KLPLTGSLX6IRVRN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWRQPYXVG43Q7DXMXH6UVWMKWGUW552F/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00036.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00034.html
- https://seclists.org/bugtraq/2020/Feb/27
- https://seclists.org/bugtraq/2020/Feb/31
- https://seclists.org/bugtraq/2021/Jan/3
- https://security.netapp.com/advisory/ntap-20200103-0002/
- https://usn.ubuntu.com/4239-1/
- https://www.debian.org/security/2020/dsa-4626
- https://www.debian.org/security/2020/dsa-4628
- https://www.tenable.com/security/tns-2021-14
- https://bugs.php.net/bug.php?id=78863
