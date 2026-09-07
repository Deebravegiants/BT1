# [M] Apache Geode web-api is vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-w595-4975-gm3h
CVE: CVE-2024-44088
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-w595-4975-gm3h
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-web-api` — affected >=1.1.0 <1.15.2

## Details
Malicious script injection ('Cross-site Scripting') vulnerability in Apache Geode web-api (REST). This vulnerability allows an attacker that tricks a logged-in user into clicking a specially-crafted link to execute code on the returned page, which could lead to theft of the user's session information and even account takeover.



This issue affects Apache Geode: all versions prior to 1.15.2.

Users are recommended to upgrade to version 1.15.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44088
- https://github.com/apache/geode
- https://lists.apache.org/thread/161r34nokmcc0w74mnf04lskgb8g1d3g
- http://www.openwall.com/lists/oss-security/2025/10/14/5
