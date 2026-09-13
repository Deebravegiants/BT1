# [C] CVE-2019-14697

## Summary
Severity: Critical
Advisory: CVE-2019-14697
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-06
Source: https://osv.dev/vulnerability/CVE-2019-14697
Type: osv

## Details
musl libc through 1.1.23 has an x87 floating-point stack adjustment imbalance, related to the math/i386/ directory. In some cases, use of this library could introduce out-of-bounds writes that are not present in an application's source code.

## References
- https://security.gentoo.org/glsa/202003-13
- http://www.openwall.com/lists/oss-security/2019/08/06/4
- https://www.openwall.com/lists/musl/2019/08/06/1
