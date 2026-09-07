# [H] Apache Tomcat allows remote attackers to bypass a CSRF protection mechanism by using a token

## Summary
Severity: High
Advisory: GHSA-w7cg-5969-678w
CVE: CVE-2015-5351
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w7cg-5969-678w
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <7.0.68
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0 <8.0.31
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M0 <9.0.0.M2

## Details
The (1) Manager and (2) Host Manager applications in Apache Tomcat 7.x before 7.0.68, 8.x before 8.0.31, and 9.x before 9.0.0.M2 establish sessions and send CSRF tokens for arbitrary new requests, which allows remote attackers to bypass a CSRF protection mechanism by using a token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5351
- https://access.redhat.com/errata/RHSA-2016:1087
- https://access.redhat.com/errata/RHSA-2016:1088
- https://bto.bluecoat.com/security-advisory/sa118
- https://github.com/apache/tomcat
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05150442
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05158626
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://security.gentoo.org/glsa/201705-09
- https://security.netapp.com/advisory/ntap-20180531-0001
- https://softwaresupport.hpe.com/document/-/facetsearch/document/KM02978021
- https://web.archive.org/web/20160321234551/http://www.securitytracker.com/id/1035069
- https://web.archive.org/web/20161020161943/http://www.securityfocus.com/bid/83330
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00069.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00085.html
- http://packetstormsecurity.com/files/135882/Apache-Tomcat-CSRF-Token-Leak.html
- http://rhn.redhat.com/errata/RHSA-2016-1089.html
- http://rhn.redhat.com/errata/RHSA-2016-2599.html
