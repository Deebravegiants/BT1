# [H] Path Traversal in Apache Camel

## Summary
Severity: High
Advisory: GHSA-4wjq-69rc-8wcp
CVE: CVE-2019-0194
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-05-02
Source: https://github.com/advisories/GHSA-4wjq-69rc-8wcp
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-core` — affected >=2.21.0 <2.21.5
- Maven: `org.apache.camel:camel-core` — affected >=2.22.0 <2.22.3
- Maven: `org.apache.camel:camel-core` — affected >=2.23.0 <2.23.1

## Details
Apache Camel's File is vulnerable to directory traversal. Camel 2.21.0 to 2.21.3, 2.22.0 to 2.22.2, 2.23.0 and the unsupported Camel 2.x (2.19 and earlier) versions may be also affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0194
- https://github.com/apache/camel/pull/2700
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-13042
- https://lists.apache.org/thread.html/0a163d02169d3d361150e8183df4af33f1a3d8a419b2937ac8e6c66f@%3Cusers.camel.apache.org%3E
- https://lists.apache.org/thread.html/45e23ade8d3cb754615f95975e89e8dc73c59eeac914f07d53acbac6@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/a39441db574ee996f829344491b3211b53c9ed926f00ae5d88943b76@%3Cdev.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/04/30/2
