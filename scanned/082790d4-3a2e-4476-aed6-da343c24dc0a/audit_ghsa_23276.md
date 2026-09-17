# [H] Deserialization of Untrusted Data in Apache OpenJPA

## Summary
Severity: High
Advisory: GHSA-j65f-mvgw-prp2
CVE: CVE-2013-1768
CWE: CWE-502
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j65f-mvgw-prp2
Type: github-advisory

## Affected
- Maven: `org.apache.openjpa:openjpa` — affected >=1.0.0 <1.2.3
- Maven: `org.apache.openjpa:openjpa` — affected >=2.0.0 <2.2.2

## Details
The BrokerFactory functionality in Apache OpenJPA 1.x before 1.2.3 and 2.x before 2.2.2 creates local executable JSP files containing logging trace data produced during deserialization of certain crafted OpenJPA objects, which makes it easier for remote attackers to execute arbitrary code by creating a serialized object and leveraging improperly secured server programs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1768
- https://github.com/apache/openjpa/commit/7f14c7df6b7c7ef42f0671138b9b5dd062fe99aa
- https://github.com/apache/openjpa/commit/87a4452be08b4f97274d0ccfac585ae85841e470
- https://github.com/apache/openjpa/commit/b8933dc24b84e7e7430ece56bd645d425dd89f24
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82268
- https://github.com/apache/openjpa
- https://seclists.org/fulldisclosure/2013/Jun/98
- http://rhn.redhat.com/errata/RHSA-2013-1862.html
- http://svn.apache.org/viewvc?view=revision&revision=1462076
- http://svn.apache.org/viewvc?view=revision&revision=1462225
- http://svn.apache.org/viewvc?view=revision&revision=1462268
- http://svn.apache.org/viewvc?view=revision&revision=1462318
- http://svn.apache.org/viewvc?view=revision&revision=1462328
- http://svn.apache.org/viewvc?view=revision&revision=1462488
- http://svn.apache.org/viewvc?view=revision&revision=1462512
- http://svn.apache.org/viewvc?view=revision&revision=1462558
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
