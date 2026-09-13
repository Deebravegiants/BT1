# [C] CVE-2016-7415

## Summary
Severity: Critical
Advisory: CVE-2016-7415
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/CVE-2016-7415
Type: osv

## Details
Stack-based buffer overflow in the Locale class in common/locid.cpp in International Components for Unicode (ICU) through 57.1 for C/C++ allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a long locale string.

## References
- http://www.openwall.com/lists/oss-security/2016/09/15/10
- http://www.securityfocus.com/bid/93022
- https://security.gentoo.org/glsa/201701-58
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.tenable.com/security/tns-2016-19
- https://bugs.php.net/bug.php?id=73007
