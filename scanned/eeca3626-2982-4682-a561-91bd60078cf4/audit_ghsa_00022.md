# [H] High severity vulnerability that affects commons-fileupload:commons-fileupload

## Summary
Severity: High
Advisory: GHSA-fvm3-cfvj-gxqq
CVE: CVE-2016-3092
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-fvm3-cfvj-gxqq
Type: github-advisory

## Affected
- Maven: `commons-fileupload:commons-fileupload` — affected >=0 <1.3.2

## Details
The MultipartStream class in Apache Commons Fileupload before 1.3.2, as used in Apache Tomcat 7.x before 7.0.70, 8.x before 8.0.36, 8.5.x before 8.5.3, and 9.x before 9.0.0.M7 and other products, allows remote attackers to cause a denial of service (CPU consumption) via a long boundary string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3092
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://web.archive.org/web/20171111060434/http://www.securitytracker.com/id/1039606
- https://web.archive.org/web/20171103224941/http://www.securitytracker.com/id/1036900
- https://web.archive.org/web/20170317103106/http://www.securitytracker.com/id/1037029
- https://web.archive.org/web/20160924080828/http://www.securityfocus.com/bid/91453
- https://web.archive.org/web/20160726114129/http://www.securitytracker.com/id/1036427
- https://security.netapp.com/advisory/ntap-20190212-0001
- https://security.gentoo.org/glsa/202107-39
- https://security.gentoo.org/glsa/201705-09
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/388a323769f1dff84c9ec905455aa73fbcb20338e3c7eb131457f708@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/388a323769f1dff84c9ec905455aa73fbcb20338e3c7eb131457f708%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/343558d982879bf88ec20dbf707f8c11255f8e219e81d45c4f8d0551@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/343558d982879bf88ec20dbf707f8c11255f8e219e81d45c4f8d0551%40%3Cdev.tomcat.apache.org%3E
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05324759
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05289840
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05204371
