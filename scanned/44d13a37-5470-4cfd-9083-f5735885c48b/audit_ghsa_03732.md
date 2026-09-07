# [C] XML External Entity Reference in Apache Karaf

## Summary
Severity: Critical
Advisory: GHSA-92wj-x78c-m4fx
CVE: CVE-2018-11788
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-07
Source: https://github.com/advisories/GHSA-92wj-x78c-m4fx
Type: github-advisory

## Affected
- Maven: `org.apache.karaf.specs:org.apache.karaf.specs.java.xml` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.karaf.specs:org.apache.karaf.specs.java.xml` — affected >=0 <4.1.7

## Details
Apache Karaf provides a features deployer, which allows users to "hot deploy" a features XML by dropping the file directly in the deploy folder. The features XML is parsed by XMLInputFactory class. Apache Karaf XMLInputFactory class doesn't contain any mitigation codes against XXE. This is a potential security risk as an user can inject external XML entities in Apache Karaf version prior to 4.1.7 or 4.2.2. It has been fixed in Apache Karaf 4.1.7 and 4.2.2 releases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11788
- https://github.com/apache/karaf/commit/0c36c50bc158739c8fc8543122a6740c54adafca
- https://github.com/apache/karaf
- https://web.archive.org/web/20200227101219/https://www.securityfocus.com/bid/106479
- http://karaf.apache.org/security/cve-2018-11788.txt
