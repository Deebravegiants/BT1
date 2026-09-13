# [H] Improper Restriction of XML External Entity Reference in org.apache.syncope:syncope-core

## Summary
Severity: High
Advisory: GHSA-qfjv-998w-q48f
CVE: CVE-2018-17186
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-qfjv-998w-q48f
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope-core` — affected >=0 <2.0.11
- Maven: `org.apache.syncope:syncope-core` — affected >=2.1.0 <2.1.2

## Details
An administrator with workflow definition entitlements can use DTD to perform malicious operations, including but not limited to file read, file write, and code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17186
- https://github.com/apache/syncope/commit/a0f35f45f8ca5c98853ae8477fb2db81a84709a
- https://github.com/advisories/GHSA-qfjv-998w-q48f
- https://syncope.apache.org/security#CVE-2018-17186:_XXE_on_BPMN_definitions
