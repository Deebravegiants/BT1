# [M] Unauthorized access to Class instance in Jinjava

## Summary
Severity: Medium
Advisory: GHSA-2hjr-fg6c-v2h6
CVE: CVE-2020-12668
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-2hjr-fg6c-v2h6
Type: github-advisory

## Affected
- Maven: `com.hubspot.jinjava:jinjava` — affected >=0 <2.5.4

## Details
Jinjava before 2.5.4 allow access to arbitrary classes by calling Java methods on objects passed into a Jinjava context. This could allow for abuse of the application class loader, including Arbitrary File Disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12668
- https://github.com/HubSpot/jinjava/pull/426/commits/5dfa5b87318744a4d020b66d5f7747acc36b213b
- https://github.com/HubSpot/jinjava/pull/435/commits/1b9aaa4b420c58b4a301cf4b7d26207f1c8d1165
- https://github.com/HubSpot/jinjava/compare/jinjava-2.5.3...jinjava-2.5.4
- https://github.com/HubSpot/jinjava/releases/tag/jinjava-2.5.4
- https://securitylab.github.com/advisories/GHSL-2020-072-hubspot_jinjava
