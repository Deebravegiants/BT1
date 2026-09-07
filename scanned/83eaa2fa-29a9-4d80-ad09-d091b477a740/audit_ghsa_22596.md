# [M] Improper Control of Generation of Code in Apache Camel

## Summary
Severity: Medium
Advisory: GHSA-x9fv-c87w-55wc
CVE: CVE-2013-4330
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x9fv-c87w-55wc
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-core` — affected >=0 <2.9.7
- Maven: `org.apache.camel:camel-core` — affected >=2.10.0 <2.10.7
- Maven: `org.apache.camel:camel-core` — affected >=2.11.0 <2.11.2
- Maven: `org.apache.camel:camel-core` — affected >=2.12.0 <2.12.1

## Details
Apache Camel before 2.9.7, 2.10.0 before 2.10.7, 2.11.0 before 2.11.2, and 2.12.0 allows remote attackers to execute arbitrary simple language expressions by including "$simple{}" in a CamelFileName message header to a (1) FILE or (2) FTP producer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4330
- https://github.com/apache/camel/commit/2281b1f365c50ee1a470fb9990b753eadee9095
- https://github.com/apache/camel/commit/27a9752a565fbef436bac4fcf22d339e3295b2a
- https://github.com/apache/camel/commit/3215fe50dd42c83a7a454dd36486843fe36eae4
- https://github.com/apache/camel/commit/5ba8f63f78f82b0cddf6cecbf59ac444a0cae2a6
- https://github.com/apache/camel/commit/ce19353f1297c5d3dc59be21a1ead89c0a44907
- https://exchange.xforce.ibmcloud.com/vulnerabilities/87542
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-6748
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf%40%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d%40%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://camel.apache.org/security-advisories.data/CVE-2013-4330.txt.asc?version=1&modificationDate=1380535446943
- http://packetstormsecurity.com/files/123454
- http://rhn.redhat.com/errata/RHSA-2013-1862.html
- http://rhn.redhat.com/errata/RHSA-2014-0124.html
- http://rhn.redhat.com/errata/RHSA-2014-0140.html
- http://rhn.redhat.com/errata/RHSA-2014-0245.html
- http://rhn.redhat.com/errata/RHSA-2014-0254.html
