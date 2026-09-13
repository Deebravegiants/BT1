# [H] Apache Linkis DataSource remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-jjvc-v8gw-5255
CVE: CVE-2023-46801
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-jjvc-v8gw-5255
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-datasource` — affected >=1.4.0 <1.6.0

## Details
In Apache Linkis <= 1.5.0, data source management module, when adding Mysql data source, exists remote code execution vulnerability for java version < 1.8.0_241. The deserialization vulnerability exploited through jrmp can inject malicious files into the server and execute them. 

This attack requires the attacker to obtain an authorized account from Linkis before it can be carried out.  We recommend that users upgrade the java version to >= 1.8.0_241. Or users upgrade Linkis to version 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46801
- https://github.com/apache/linkis
- https://linkis.apache.org/download/release-notes-1.6.0
- https://lists.apache.org/thread/0dnzh64xy1n7qo3rgo2loz9zn7m9xgdx
