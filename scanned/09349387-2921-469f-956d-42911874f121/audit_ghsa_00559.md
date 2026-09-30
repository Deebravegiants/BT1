# [M] Exposure of Sensitive Information to an Unauthorized Actor in Apache syncope-cope

## Summary
Severity: Medium
Advisory: GHSA-v3vf-2r98-xw8w
CVE: CVE-2018-1322
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-v3vf-2r98-xw8w
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope-core` — affected >=0 <1.2.11
- Maven: `org.apache.syncope:syncope-core` — affected >=2.0.0 <2.0.8

## Details
An administrator with user search entitlements in Apache Syncope 1.2.x before 1.2.11 and 2.0.x before 2.0.8 can recover sensitive security values using the fiql and orderby parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1322
- https://github.com/apache/syncope/commit/44a5ca0fbd357b8b5d81aa9313fb01cca30d8ad
- https://github.com/apache/syncope/commit/735579b6f987b407049ac1f1da08e675d957c3e
- https://github.com/advisories/GHSA-v3vf-2r98-xw8w
- https://github.com/apache/syncope
- https://www.exploit-db.com/exploits/45400
- http://syncope.apache.org/security.html#CVE-2018-1322:_Information_disclosure_via_FIQL_and_ORDER_BY_sorting
- http://www.securityfocus.com/bid/103507
