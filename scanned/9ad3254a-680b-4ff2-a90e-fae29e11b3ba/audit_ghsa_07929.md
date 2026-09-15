# [H] Apache Camel Deserializes Untrusted Data in its LevelDB Component

## Summary
Severity: High
Advisory: GHSA-429q-mrc4-38fr
CVE: CVE-2026-25747
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-429q-mrc4-38fr
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-leveldb` — affected >=3.0.0 <4.10.9
- Maven: `org.apache.camel:camel-leveldb` — affected >=4.11.0 <4.14.5
- Maven: `org.apache.camel:camel-leveldb` — affected >=4.15.0 <4.18.0

## Details
Deserialization of Untrusted Data vulnerability in Apache Camel LevelDB component.

The Camel-LevelDB DefaultLevelDBSerializer class deserializes data read from the LevelDB aggregation repository using java.io.ObjectInputStream without applying any ObjectInputFilter or class-loading restrictions. An attacker who can write to the LevelDB database files used by a Camel application can inject a crafted serialized Java object that, when deserialized during normal aggregation repository operations, results in arbitrary code execution in the context of the application.
This issue affects Apache Camel: from 4.10.0 before 4.10.8, from 4.14.0 before 4.14.5, from 4.15.0 before 4.18.0.

Users are recommended to upgrade to version 4.18.0, which fixes the issue. For the 4.10.x LTS releases, users are recommended to upgrade to 4.10.9, while for 4.14.x LTS releases, users are recommended to upgrade to 4.14.5

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25747
- https://github.com/apache/camel/commit/0e3ac39e20416c91af6df2cfce3f7d795e75ad89
- https://github.com/apache/camel/commit/5f343367f7b25646b7d12be26c3e87381c7a7ecb
- https://github.com/apache/camel/commit/af2f2e9571b3b03a36b771bd9eb10427886d9636
- https://camel.apache.org/security/CVE-2026-25747.html
- https://github.com/apache/camel
- https://github.com/oscerd/CVE-2026-25747
- https://issues.apache.org/jira/browse/CAMEL-22966
- http://www.openwall.com/lists/oss-security/2026/02/18/6
