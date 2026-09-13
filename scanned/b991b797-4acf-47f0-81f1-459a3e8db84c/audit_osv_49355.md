# [C] CVE-2019-11037

## Summary
Severity: Critical
Advisory: CVE-2019-11037
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-03
Source: https://osv.dev/vulnerability/CVE-2019-11037
Type: osv

## Details
In PHP imagick extension in versions between 3.3.0 and 3.4.4, writing to an array of values in ImagickKernel::fromMatrix() function did not check that the address will be within the allocated array. This could lead to out of bounds write to memory if the function is called with the data controlled by untrusted party.

## References
- http://www.securityfocus.com/bid/108292
- https://usn.ubuntu.com/4586-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MQ7WJA25YF2R2LRALK4QEYWUHHJPSUD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BU66V7QJKD32RXLY5J7Z5NZH4V3VV524/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FME5ZG7DDYWUPPHTTAFJB5OFFCPXYHPS/
- https://seclists.org/bugtraq/2019/Nov/39
- https://security.gentoo.org/glsa/202003-38
- https://bugs.php.net/bug.php?id=77791
- https://www.debian.org/security/2019/dsa-4576
- https://github.com/CVEProject/cvelist/pull/1964
