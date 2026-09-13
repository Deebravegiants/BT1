# [H] CVE-2017-7868

## Summary
Severity: High
Advisory: CVE-2017-7868
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7868
Type: osv

## Details
International Components for Unicode (ICU) for C/C++ before 2017-02-13 has an out-of-bounds write caused by a heap-based buffer overflow related to the utf8TextAccess function in common/utext.cpp and the utext_moveIndex32* function.

## References
- http://www.debian.org/security/2017/dsa-3830
- http://www.securityfocus.com/bid/97674
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=437
- https://security.gentoo.org/glsa/201710-03
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://bugs.icu-project.org/trac/changeset/39671
