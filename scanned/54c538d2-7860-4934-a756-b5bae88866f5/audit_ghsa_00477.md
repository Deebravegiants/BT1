# [C] Camel-xstream component in Apache Camel can allow remote attackers to execute arbitrary commands 

## Summary
Severity: Critical
Advisory: GHSA-gv5f-cjw9-5vxg
CVE: CVE-2015-5344
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-gv5f-cjw9-5vxg
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-xstream` — affected >=0 <2.15.5
- Maven: `org.apache.camel:camel-xstream` — affected >=2.16.0 <2.16.1

## Details
The camel-xstream component in Apache Camel before 2.15.5 and 2.16.x before 2.16.1 allow remote attackers to execute arbitrary commands via a crafted serialized Java object in an HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5344
- https://github.com/apache/camel/commit/157c0b4a3c8017de432f1c99f83e374e97dc4d36
- https://github.com/apache/camel/commit/369d0a6d605055cb843e7962b101e3bbcd113fec
- https://github.com/apache/camel/commit/4491c080cb6c8659fc05441e49307b7d4349aa56
- https://github.com/apache/camel/commit/4cdc6b177ee7391eedc9f0b695c05d56f84b0812
- https://github.com/apache/camel/commit/8386d8f7260143802553bc6dbae2880d6c0bafda
- https://github.com/apache/camel/commit/b7afb3769a38b8e526f8046414d4a71430d77df0
- https://github.com/apache/camel/commit/f07a33c467adb3d37aa8192698caadfee43a17dc
- https://github.com/advisories/GHSA-gv5f-cjw9-5vxg
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-9297
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://camel.apache.org/security-advisories.data/CVE-2015-5344.txt.asc
- http://rhn.redhat.com/errata/RHSA-2016-2035.html
- http://www.securityfocus.com/archive/1/537414/100/0/threaded
- http://www.securityfocus.com/bid/82260
