# [C] Camel-castor component in Apache Camel is vulnerable to Java object de-serialisation

## Summary
Severity: Critical
Advisory: GHSA-vf4q-8mr7-5c5c
CVE: CVE-2017-12634
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-vf4q-8mr7-5c5c
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-castor` — affected >=2.0.0 <2.19.4
- Maven: `org.apache.camel:camel-castor` — affected >=2.20.0 <2.20.1

## Details
The camel-castor component in Apache Camel 2.x before 2.19.4 and 2.20.x before 2.20.1 is vulnerable to Java object de-serialisation vulnerability. De-serializing untrusted data can lead to security flaws.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12634
- https://github.com/apache/camel/commit/2ae645e90edff3bcc1b958cb53ddc5e60a7f49fd
- https://github.com/apache/camel/commit/573ebd3de810cc7e239f175e1d2d6993f1f2ad08
- https://github.com/apache/camel/commit/ad3c1ce9d8300c339cfa7d0f4a4dea691a947988
- https://github.com/apache/camel/commit/adc06a78f04c8d798709a5818104abe5a8ae4b38
- https://github.com/apache/camel/commit/bdff8f3f3583e4f14cdaf24f2037e0fbef252630
- https://github.com/apache/camel/commit/c613905e95a3dab87158d9526aea9439f2de9621
- https://access.redhat.com/errata/RHSA-2018:0319
- https://github.com/advisories/GHSA-vf4q-8mr7-5c5c
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-11929
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://camel.apache.org/security-advisories.data/CVE-2017-12634.txt.asc
- http://www.securityfocus.com/bid/101876
