# [C] CVE-2016-5873

## Summary
Severity: Critical
Advisory: CVE-2016-5873
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-5873
Type: osv

## Details
Buffer overflow in the HTTP URL parsing functions in pecl_http before 3.0.1 might allow remote attackers to execute arbitrary code via non-printable characters in a URL.

## References
- http://www.securityfocus.com/bid/95863
- http://www.openwall.com/lists/oss-security/2016/06/29/4
- https://pecl.php.net/package/pecl_http/3.0.1
- https://security.gentoo.org/glsa/201612-17
- https://security.netapp.com/advisory/ntap-20180112-0001/
- http://www.openwall.com/lists/oss-security/2016/06/29/1
- https://github.com/m6w6/ext-http/commit/3724cd76a28be1d6049b5537232e97ac
- https://bugs.php.net/bug.php?id=71719
