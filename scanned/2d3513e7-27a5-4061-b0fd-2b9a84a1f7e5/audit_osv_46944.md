# [H] CVE-2015-8393

## Summary
Severity: High
Advisory: CVE-2015-8393
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2015-12-02
Source: https://osv.dev/vulnerability/CVE-2015-8393
Type: osv

## Details
pcregrep in PCRE before 8.38 mishandles the -q option for binary files, which might allow remote attackers to obtain sensitive information via a crafted file, as demonstrated by a CGI script that sends stdout data to a client.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174931.html
- http://vcs.pcre.org/pcre/code/trunk/ChangeLog?view=markup
- http://www.openwall.com/lists/oss-security/2015/11/29/1
- http://www.securityfocus.com/bid/82990
- https://bto.bluecoat.com/security-advisory/sa128
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://security.gentoo.org/glsa/201607-02
- https://security.netapp.com/advisory/ntap-20230216-0002/
- http://www.openwall.com/lists/oss-security/2015/11/29/1
