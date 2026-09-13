# [C] CVE-2015-8394

## Summary
Severity: Critical
Advisory: CVE-2015-8394
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2015-12-02
Source: https://osv.dev/vulnerability/CVE-2015-8394
Type: osv

## Details
PCRE before 8.38 mishandles the (?(<digits>) and (?(R<digits>) conditions, which allows remote attackers to cause a denial of service (integer overflow) or possibly have unspecified other impact via a crafted regular expression, as demonstrated by a JavaScript RegExp object encountered by Konqueror.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174931.html
- http://www.openwall.com/lists/oss-security/2015/11/29/1
- http://www.securityfocus.com/bid/82990
- https://bto.bluecoat.com/security-advisory/sa128
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://security.gentoo.org/glsa/201607-02
- https://security.netapp.com/advisory/ntap-20230216-0002/
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174931.html
- http://www.openwall.com/lists/oss-security/2015/11/29/1
- https://bto.bluecoat.com/security-advisory/sa128
- http://vcs.pcre.org/pcre/code/trunk/ChangeLog?view=markup
