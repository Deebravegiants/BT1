# [M] Cross-Site Request Forgery in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-76vr-72mv-mf3q
CVE: CVE-2012-4431
CWE: CWE-352
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-76vr-72mv-mf3q
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.36
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.32

## Details
org/apache/catalina/filters/CsrfPreventionFilter.java in Apache Tomcat 6.x before 6.0.36 and 7.x before 7.0.32 allows remote attackers to bypass the cross-site request forgery (CSRF) protection mechanism via a request that lacks a session identifier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4431
- https://github.com/apache/tomcat
- https://h20566.www2.hp.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c03748878
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A18541
- http://lists.opensuse.org/opensuse-updates/2012-12/msg00089.html
- http://lists.opensuse.org/opensuse-updates/2012-12/msg00090.html
- http://lists.opensuse.org/opensuse-updates/2013-01/msg00037.html
- http://lists.opensuse.org/opensuse-updates/2013-01/msg00051.html
- http://lists.opensuse.org/opensuse-updates/2013-01/msg00080.html
- http://marc.info/?l=bugtraq&m=136612293908376&w=2
- http://marc.info/?l=bugtraq&m=139344343412337&w=2
- http://rhn.redhat.com/errata/RHSA-2013-0267.html
- http://rhn.redhat.com/errata/RHSA-2013-0268.html
- http://rhn.redhat.com/errata/RHSA-2013-0647.html
- http://rhn.redhat.com/errata/RHSA-2013-0648.html
- http://rhn.redhat.com/errata/RHSA-2013-1853.html
- http://svn.apache.org/viewvc/tomcat/tc7.0.x/trunk/java/org/apache/catalina/filters/CsrfPreventionFilter.java?r1=1393088&r2=1393087&pathrev=1393088
- http://svn.apache.org/viewvc/tomcat/tc7.0.x/trunk/webapps/docs/changelog.xml?r1=1393088&r2=1393087&pathrev=1393088
- http://svn.apache.org/viewvc?view=revision&revision=1393088
- http://tomcat.apache.org/security-6.html
