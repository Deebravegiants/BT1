# [M] Liferay Portal's Incorrect Authorization vulnerability can lead to guest users to obtaining sensitive data

## Summary
Severity: Medium
Advisory: GHSA-fvp7-jj9m-3qpf
CVE: CVE-2025-43784
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-fvp7-jj9m-3qpf
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.headless.builder.impl` — affected >=0 <1.0.32

## Details
An Improper Access Control vulnerability in Liferay Portal  7.4.0 through 7.4.3.124, and Liferay DXP 2024.Q2.0 through 2024.Q2.8, 2024.Q1.1 through 2024.Q1.12 and 7.4 GA through update 92 allows guest users to obtain object entry information via the API Builder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43784
- https://github.com/liferay/liferay-portal/commit/ccbae813d4a9ec66597191f58d1cb4137f264c99
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18066
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43784
