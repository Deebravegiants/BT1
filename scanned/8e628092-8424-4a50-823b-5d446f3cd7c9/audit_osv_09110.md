# [C] CVE-2016-7950

## Summary
Severity: Critical
Advisory: CVE-2016-7950
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7950
Type: osv

## Details
The XRenderQueryFilters function in X.org libXrender before 0.9.10 allows remote X servers to trigger out-of-bounds write operations via vectors involving filter name lengths.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93369
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libXrender/commit/?id=8fad00b0b647ee662ce4737ca15be033b7a21714
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7WCKZFMZ76APAVMIRCUKKHEB4GAS7ZUP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZHUT5YOSWVMBJNWZGUQNZRBFIZKRM4A6/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://security.gentoo.org/glsa/201704-03
