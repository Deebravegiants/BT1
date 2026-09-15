# [M] Apache Syncope: Console XXE on Keymaster parameters

## Summary
Severity: Medium
Advisory: GHSA-73f3-rqqf-2j54
CVE: CVE-2026-23795
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-73f3-rqqf-2j54
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.client.idrepo:syncope-client-idrepo-console` — affected >=3.0.0 <3.0.16
- Maven: `org.apache.syncope.client.idrepo:syncope-client-idrepo-console` — affected >=4.0.0 <4.0.4

## Details
Improper Restriction of XML External Entity Reference vulnerability in Apache Syncope Console. An administrator with adequate entitlements to create or edit Keymaster parameters via Console can construct malicious XML text to launch an XXE attack, thereby causing sensitive data leakage occurs.

This issue affects Apache Syncope: from 3.0 through 3.0.15, from 4.0 through 4.0.3.

Users are recommended to upgrade to version 3.0.16 / 4.0.4, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23795
- https://github.com/apache/syncope
- https://lists.apache.org/thread/mzgbdn8hzk8vr94o660njcc7w62c2pos
- http://www.openwall.com/lists/oss-security/2026/02/02/2
