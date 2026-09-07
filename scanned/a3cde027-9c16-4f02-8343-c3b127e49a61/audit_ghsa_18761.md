# [H] Apache Geode: CSRF attacks through GET requests to the Management and Monitoring REST API that can execute gfsh commands on the target system

## Summary
Severity: High
Advisory: GHSA-gjp8-99fv-cgcw
CVE: CVE-2025-47410
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-18
Source: https://github.com/advisories/GHSA-gjp8-99fv-cgcw
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-web` — affected >=1.10.0 <1.15.2

## Details
Apache Geode is vulnerable to CSRF attacks through GET requests to the Management and Monitoring REST API that could allow an attacker who has tricked a user into giving up their Geode session credentials to submit malicious commands on the target system on behalf of the authenticated user.


This issue affects Apache Geode: versions 1.10 through 1.15.1

Users are recommended to upgrade to version 1.15.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47410
- https://github.com/apache/geode/commit/570990909e6fd1e491f01471ad30ee3c2dbff72c
- https://github.com/apache/geode
- https://lists.apache.org/thread/k88tv3rhl4ymsvt4h6qsv7sq10q5prrt
- http://www.openwall.com/lists/oss-security/2025/10/17/2
