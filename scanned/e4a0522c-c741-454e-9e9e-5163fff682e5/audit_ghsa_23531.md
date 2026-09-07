# [M] Apache Tomcat XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p57v-p3fx-qgwm
CVE: CVE-2006-7195
CWE: CWE-79, CWE-80
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-p57v-p3fx-qgwm
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.0.0
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.18

## Details
Cross-site scripting (XSS) vulnerability in implicit-objects.jsp in Apache Tomcat 5.0.0 through 5.0.30 and 5.5.0 through 5.5.17 allows remote attackers to inject arbitrary web script or HTML via certain header values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-7195
- https://access.redhat.com/errata/RHSA-2007:0326
- https://access.redhat.com/errata/RHSA-2007:0327
- https://access.redhat.com/errata/RHSA-2007:0328
- https://access.redhat.com/errata/RHSA-2007:0340
- https://access.redhat.com/errata/RHSA-2008:0261
- https://access.redhat.com/errata/RHSA-2008:0524
- https://access.redhat.com/security/cve/CVE-2006-7195
- https://bugzilla.redhat.com/show_bug.cgi?id=237081
- https://github.com/apache/tomcat
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A10514
- https://web.archive.org/web/20080515114843/http://www.securityfocus.com/bid/28481
- https://web.archive.org/web/20171015140308/http://www.securityfocus.com/archive/1/500396/100/0/threaded
- https://web.archive.org/web/20171015140313/http://www.securityfocus.com/archive/1/500412/100/0/threaded
- https://web.archive.org/web/20201021082255/http://www.securityfocus.com/archive/1/485938/100/0/threaded
- https://web.archive.org/web/20230518052431/http://lists.vmware.com/pipermail/security-announce/2008/000003.html
- http://support.avaya.com/elmodocs2/security/ASA-2007-206.htm
- http://tomcat.apache.org/security-5.html
- http://www.redhat.com/support/errata/RHSA-2007-0327.html
- http://www.redhat.com/support/errata/RHSA-2008-0261.html
