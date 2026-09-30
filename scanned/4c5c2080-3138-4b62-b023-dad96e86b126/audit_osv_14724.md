# [M] CVE-2019-11046

## Summary
Severity: Medium
Advisory: CVE-2019-11046
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-11046
Type: osv

## Details
In PHP versions 7.2.x below 7.2.26, 7.3.x below 7.3.13 and 7.4.0, PHP bcmath extension functions on some systems, including Windows, can be tricked into reading beyond the allocated space by supplying it with string containing characters that are identified as numeric by the OS but aren't ASCII numbers. This can read to disclosure of the content of some memory locations.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N7GCOAE6KVHYJ3UQ4KLPLTGSLX6IRVRN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWRQPYXVG43Q7DXMXH6UVWMKWGUW552F/
- https://support.f5.com/csp/article/K48866433?utm_source=f5support&amp%3Butm_medium=RSS
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
- https://bugs.php.net/bug.php?id=78878
