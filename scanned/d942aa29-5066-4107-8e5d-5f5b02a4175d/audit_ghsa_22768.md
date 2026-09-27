# [M] Improper Verification of Source of a Communication Channel in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-9hjv-9h75-xmpp
CVE: CVE-2016-0763
CWE: CWE-940
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9hjv-9h75-xmpp
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.68
- Maven: `org.apache.tomcat:tomcat` — affected >=8.0.0 <8.0.32
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0M1 <9.0.0.M3

## Details
The `setGlobalContext` method in `org/apache/naming/factory/ResourceLinkFactory.java` in Apache Tomcat 7.x before 7.0.68, 8.x before 8.0.31, and 9.x before 9.0.0.M3 does not consider whether ResourceLinkFactory.setGlobalContext callers are authorized, which allows remote authenticated users to bypass intended SecurityManager restrictions and read or write to arbitrary application data, or cause a denial of service (application disruption), via a web application that sets a crafted global context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0763
- https://github.com/apache/tomcat/commit/76ebc9007567c8326217dd94844540e1e27d8468
- https://github.com/apache/tomcat/commit/c08641da04d31f730b56b8675301e55db97dfe88
- https://github.com/apache/tomcat80/commit/0531f7aeff1999d362e0a68512a3517f2cf1a6ae
- https://web.archive.org/web/20160404202803/http://www.securitytracker.com/id/1035069
- https://web.archive.org/web/20160314101138/http://www.securityfocus.com/bid/83326
- https://security.netapp.com/advisory/ntap-20180531-0001
- https://security.gentoo.org/glsa/201705-09
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/343558d982879bf88ec20dbf707f8c11255f8e219e81d45c4f8d0551@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/343558d982879bf88ec20dbf707f8c11255f8e219e81d45c4f8d0551%40%3Cdev.tomcat.apache.org%3E
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05324755
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05158626
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05150442
- https://github.com/apache/tomcat
- https://bto.bluecoat.com/security-advisory/sa118
- https://access.redhat.com/errata/RHSA-2016:1088
- https://access.redhat.com/errata/RHSA-2016:1087
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179356.html
