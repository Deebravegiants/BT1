# [C] CVE-2016-8859

## Summary
Severity: Critical
Advisory: CVE-2016-8859
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-8859
Type: osv

## Details
Multiple integer overflows in the TRE library and musl libc allow attackers to cause memory corruption via a large number of (1) states or (2) tags, which triggers an out-of-bounds write.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00041.html
- http://www.openwall.com/lists/oss-security/2016/10/19/10
- http://www.securityfocus.com/bid/93795
- https://security.gentoo.org/glsa/201701-11
- https://security.gentoo.org/glsa/202007-43
- http://www.openwall.com/lists/oss-security/2016/10/19/1
