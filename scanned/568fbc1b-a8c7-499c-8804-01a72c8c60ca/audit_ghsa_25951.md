# [C] XML External Entity Reference in Hazelcast

## Summary
Severity: Critical
Advisory: GHSA-99wh-973f-779p
CVE: CVE-2022-0265
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-99wh-973f-779p
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=5.1-beta1 <5.1

## Details
The AbstractXmlConfigRootTagRecognizer() function makes use of SAXParser generated from a SAXParserFactory with no FEATURE_SECURE_PROCESSING set, allowing for XXE attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0265
- https://github.com/hazelcast/hazelcast/pull/20407
- https://github.com/hazelcast/hazelcast/commit/4d6b666cd0291abd618c3b95cdbb51aa4208e748
- https://github.com/hazelcast/hazelcast
- https://huntr.dev/bounties/d63972a2-b910-480a-a86b-d1f75d24d563
