# [M] CVE-2017-16231

## Summary
Severity: Medium
Advisory: CVE-2017-16231
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2017-16231
Type: osv

## Details
In PCRE 8.41, after compiling, a pcretest load test PoC produces a crash overflow in the function match() in pcre_exec.c because of a self-recursive call. NOTE: third parties dispute the relevance of this report, noting that there are options that can be used to limit the amount of stack that is used

## References
- http://seclists.org/fulldisclosure/2018/Dec/33
- http://www.openwall.com/lists/oss-security/2017/11/01/11
- http://www.openwall.com/lists/oss-security/2017/11/01/7
- http://www.securityfocus.com/bid/101688
- http://packetstormsecurity.com/files/150897/PCRE-8.41-Buffer-Overflow.html
- https://bugs.exim.org/show_bug.cgi?id=2047
- http://www.openwall.com/lists/oss-security/2017/11/01/3
- http://www.openwall.com/lists/oss-security/2017/11/01/8
