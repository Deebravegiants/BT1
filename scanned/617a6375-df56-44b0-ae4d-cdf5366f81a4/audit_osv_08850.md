# [H] CVE-2016-6323

## Summary
Severity: High
Advisory: CVE-2016-6323
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-07
Source: https://osv.dev/vulnerability/CVE-2016-6323
Type: osv

## Details
The makecontext function in the GNU C Library (aka glibc or libc6) before 2.25 creates execution contexts incompatible with the unwinder on ARM EABI (32-bit) platforms, which might allow context-dependent attackers to cause a denial of service (hang), as demonstrated by applications compiled using gccgo, related to backtrace generation.

## References
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.securityfocus.com/bid/92532
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KTXSOVCRDGBIB4WCIDAGYYUBESXZ4IGK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LVWSAZVBTLALXF4SCBPDV3FY6J22DXLZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WO7IMEYWZ2WTXGGMZBWWSDCUMFN63XOB/
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=9e2ff6c9cc54c0b4402b8d49e4abe7000fde7617
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00009.html
- http://www.openwall.com/lists/oss-security/2016/08/18/12
- https://security.gentoo.org/glsa/201706-19
- https://sourceware.org/bugzilla/show_bug.cgi?id=20435
