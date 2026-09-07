# [H] Liferay Portal: Missing Rate Limiting in GraphQL Endpoint Enables Resource Exhaustion Attack

## Summary
Severity: High
Advisory: GHSA-f3hf-r62c-mfrj
CVE: CVE-2025-43796
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-f3hf-r62c-mfrj
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.vulcan.api` — affected >=8.0.2 <40.2.0
- Maven: `com.liferay:com.liferay.portal.vulcan.impl` — affected >=5.0.7 <5.0.105

## Details
Liferay Portal 7.4.0 through 7.4.3.101, and Liferay DXP 2023.Q3.0 through 2023.Q3.4, 7.4 GA through update 92 and 7.3 GA though update 35 does not limit the number of objects returned from a GraphQL queries, which allows remote attackers to perform denial-of-service (DoS) attacks on the application by executing queries that return a large number of objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43796
- https://github.com/liferay/liferay-portal/commit/2e4adf041e31f3474a14c29b7c135693f6529400
- https://github.com/liferay/liferay-portal/commit/2f74f23982fb03238f9b4ae145c33a9c1084f07e
- https://github.com/liferay/liferay-portal/commit/3780804b0d8f4f14bfca470a3e2e662bc6cef588
- https://github.com/liferay/liferay-portal/commit/8344aec3bebcd2ca409794523d5db5be6047c3dd
- https://github.com/liferay/liferay-portal/commit/83e77963499d4d3e7cc82cc48e63c992f6f29a6d
- https://github.com/liferay/liferay-portal/commit/8dda4adc0e9e7b6f82d4b3959592cad61640309b
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43796
- http://github.com/liferay/liferay-portal/commit/8f7eb98e05a5ea6961346ecc21fd73e4b46bba99
