# [C] CVE-2016-6293

## Summary
Severity: Critical
Advisory: CVE-2016-6293
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6293
Type: osv

## Details
The uloc_acceptLanguageFromHTTP function in common/uloc.cpp in International Components for Unicode (ICU) through 57.1 for C/C++ does not ensure that there is a '\0' character at the end of a certain temporary array, which allows remote attackers to cause a denial of service (out-of-bounds read) or possibly have unspecified other impact via a call with a long httpAcceptLanguage argument.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=aa82e99ed8003c01f1ef4f0940e56b85c5b032d4
- http://www.securityfocus.com/bid/92127
- https://security.gentoo.org/glsa/201701-58
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://bugs.php.net/72533
- http://openwall.com/lists/oss-security/2016/07/24/2
