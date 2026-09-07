# [M] Apache Syncope: Reflected XSS on Enduser Login

## Summary
Severity: Medium
Advisory: GHSA-v84m-gfw5-hm2w
CVE: CVE-2026-23794
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-v84m-gfw5-hm2w
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.client.idrepo:syncope-client-idrepo-common-ui` — affected >=3.0.0 <3.0.16
- Maven: `org.apache.syncope.client.idrepo:syncope-client-idrepo-common-ui` — affected >=4.0.0 <4.0.4

## Details
Reflected XSS in Apache Syncope's Enduser Login page.

An attacker that tricks a legitimate user into clicking a malicious link and logging in to Syncope Enduser could steal that user's credentials.

This issue affects Apache Syncope: from 3.0 through 3.0.15, from 4.0 through 4.0.3.

Users are recommended to upgrade to version 3.0.16 / 4.0.4, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23794
- https://github.com/apache/syncope
- https://lists.apache.org/thread/7h30ghqdsf3spl3h7gdmscxofrm8ygjo
- http://www.openwall.com/lists/oss-security/2026/02/02/1
