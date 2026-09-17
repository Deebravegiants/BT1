# [H] CVE-2016-4472

## Summary
Severity: High
Advisory: CVE-2016-4472
Aliases: PSF-2016-6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/CVE-2016-4472
Type: osv

## Details
The overflow protection in Expat is removed by compilers with certain optimization settings, which allows remote attackers to cause a denial of service (crash) or possibly execute arbitrary code via crafted XML data.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-1283 and CVE-2015-2716.

## References
- http://www.securityfocus.com/bid/91528
- http://www.ubuntu.com/usn/USN-3013-1
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://security.gentoo.org/glsa/201701-21
- https://www.tenable.com/security/tns-2016-20
- https://bugzilla.redhat.com/show_bug.cgi?id=1344251
- https://sourceforge.net/p/expat/code_git/ci/f0bec73b018caa07d3e75ec8dd967f3785d71bde
