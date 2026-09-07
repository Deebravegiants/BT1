# [M] Apache Tomcat affected by infinite loop in Double.parseDouble method in Java Runtime Environment

## Summary
Severity: Medium
Advisory: GHSA-gvgc-rxmh-5hvw
CVE: CVE-2010-4476
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gvgc-rxmh-5hvw
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.7
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.32
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.33

## Details
The `Double.parseDouble` method in Java Runtime Environment (JRE) in Oracle Java SE and Java for Business 6 Update 23 and earlier, 5.0 Update 27 and earlier, and 1.4.2_29 and earlier, as used in OpenJDK, Apache, JBossweb, and other products, allows remote attackers to cause a denial of service via a crafted string that triggers an infinite loop of estimations during conversion to a double-precision binary floating-point number, as demonstrated using 2.2250738585072012e-308.

Apache Tomcat introduced workarounds to avoid being affected by this issue in versions 7.0.7, 6.0.32, and 5.5.33.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4476
- https://github.com/apache/tomcat/commit/407841c426dc52a4c6b8ccd297df6c484a540056
- https://github.com/apache/tomcat/commit/69ef147c4498397e8f644a0699cf588b45a05120
- https://github.com/apache/tomcat/commit/b0c1eeaa0d303bcb42651b222037e079d0634c01
- https://github.com/apache/tomcat
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A12662
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A12745
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A14328
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A14589
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A19493
- https://svn.apache.org/viewvc?view=revision&revision=1066244
- https://svn.apache.org/viewvc?view=revision&revision=1066315
- https://svn.apache.org/viewvc?view=revision&revision=1066318
- https://tomcat.apache.org/security-5.html
- https://tomcat.apache.org/security-6.html
- https://tomcat.apache.org/security-7.html
- http://blog.fortify.com/blog/2011/02/08/Double-Trouble
- http://blogs.oracle.com/security/2011/02/security_alert_for_cve-2010-44.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/053926.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/053934.html
