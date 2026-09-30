# [C] Apache Camel's camel-snakeyaml component is vulnerable to Java object de-serialization

## Summary
Severity: Critical
Advisory: GHSA-hvpr-9cr6-q5v7
CVE: CVE-2017-3159
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-hvpr-9cr6-q5v7
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-snakeyaml` — affected >=0 <2.17.5
- Maven: `org.apache.camel:camel-snakeyaml` — affected >=2.18.0 <2.18.2

## Details
Apache Camel's camel-snakeyaml component is vulnerable to Java object de-serialization. De-serializing untrusted data can lead to security flaws.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3159
- https://github.com/apache/camel/commit/20e26226107f3133c87d0f5c845e02f824823f69
- https://github.com/apache/camel/commit/21c04b635cacd57bf4d438fc2308533ca1babde9
- https://github.com/apache/camel/commit/2f19ce59cc4d89f21455f47604915fab6a22233b
- https://github.com/apache/camel/commit/6b979d07fd4be6ac913368f2abeae690d3325d37
- https://github.com/apache/camel/commit/bea972e99b5c75dc0edeb93ecbba9ff70c36bb43
- https://github.com/apache/camel/commit/c98e48a7421b813bd47d5ae2717aea35a98d187
- https://github.com/apache/camel/commit/dcb5a74a3987d2264ad195c7844bbb6c8121661
- https://access.redhat.com/errata/RHSA-2017:0868
- https://github.com/advisories/GHSA-hvpr-9cr6-q5v7
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-10575
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- https://www.github.com/mbechler/marshalsec/blob/master/marshalsec.pdf?raw=true
- http://camel.apache.org/security-advisories.data/CVE-2017-3159.txt.asc?version=1&modificationDate=1486565167000&api=v2
- http://www.openwall.com/lists/oss-security/2017/05/22/2
- http://www.securityfocus.com/bid/96321
