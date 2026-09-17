# [H] Deserialization of Untrusted Data in Apache Camel SQL

## Summary
Severity: High
Advisory: GHSA-36xr-4x2f-cfj9
CVE: CVE-2024-22369
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-36xr-4x2f-cfj9
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-sql` — affected >=3.0.0 <3.21.4
- Maven: `org.apache.camel:camel-sql` — affected >=3.22.0 <3.22.1
- Maven: `org.apache.camel:camel-sql` — affected >=4.0.0 <4.0.4
- Maven: `org.apache.camel:camel-sql` — affected >=4.1.0 <4.4.0

## Details
Deserialization of Untrusted Data vulnerability in Apache Camel SQL Component. This issue affects Apache Camel: from 3.0.0 before 3.21.4, from 3.22.0 before 3.22.1, from 4.0.0 before 4.0.4, from 4.1.0 before 4.4.0.

Users are recommended to upgrade to version 4.4.0, which fixes the issue. If users are on the 4.0.x LTS releases stream, then they are suggested to upgrade to 4.0.4. If users are on 3.x, they are suggested to move to 3.21.4 or 3.22.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22369
- https://github.com/apache/camel/pull/12706
- https://github.com/apache/camel/pull/12707
- https://github.com/apache/camel/pull/12708
- https://github.com/apache/camel/pull/12709
- https://github.com/apache/camel/pull/12716
- https://github.com/apache/camel/pull/12717
- https://github.com/apache/camel/pull/12718
- https://github.com/apache/camel/pull/12719
- https://github.com/apache/camel/pull/12789
- https://github.com/apache/camel
- https://github.com/oscerd/CVE-2024-22369
- https://issues.apache.org/jira/browse/CAMEL-20303
- https://lists.apache.org/thread/3dko781dy2gy5l3fs48p56fgp429yb0f
