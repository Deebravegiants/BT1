# [H] Deserialization of Untrusted Data in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-v6c7-8qx5-8gmp
CVE: CVE-2013-2185
CWE: CWE-502
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v6c7-8qx5-8gmp
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <7.0.39

## Details
The readObject method in the DiskFileItem class in Apache Tomcat and JBoss Web, as used in Red Hat JBoss Enterprise Application Platform 6.1.0 and Red Hat JBoss Portal 6.0.0, allows remote attackers to write to arbitrary files via a NULL byte in a file name in a serialized instance, a similar issue to CVE-2013-2186.  

NOTE: this issue is reportedly disputed by the Apache Tomcat team, although Red Hat considers it a vulnerability. The dispute appears to regard whether it is the responsibility of applications to avoid providing untrusted data to be deserialized, or whether this class should inherently protect against this issue. Regardless the tomcat maintainers have altered the behavior of this method in version 7.0.39.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2185
- https://github.com/apache/tomcat
- http://openwall.com/lists/oss-security/2014/10/24/12
- http://rhn.redhat.com/errata/RHSA-2013-1193.html
- http://rhn.redhat.com/errata/RHSA-2013-1194.html
- http://rhn.redhat.com/errata/RHSA-2013-1265.html
- http://www.openwall.com/lists/oss-security/2013/09/05/4
