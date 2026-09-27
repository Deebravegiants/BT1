# [H] Liferay Portal SessionClicks does not restrict the saving of request parameters in the HTTP session

## Summary
Severity: High
Advisory: GHSA-mf3r-6m25-3867
CVE: CVE-2025-3526
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-mf3r-6m25-3867
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.kernel` — affected >=0 <38.0.0

## Details
SessionClicks in Liferay Portal 7.0.0 through 7.4.3.21, and Liferay DXP 7.4 GA through update 9, 7.3 GA through update 25, and older unsupported versions does not restrict the saving of request parameters in the HTTP session, which allows remote attackers to consume system memory leading to denial-of-service (DoS) conditions via crafted HTTP requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3526
- https://github.com/liferay/liferay-portal/commit/429834b7cf7c131576f196466a386bb6ce764716
- https://github.com/liferay/liferay-portal/commit/b40fe110eb9d264c9c1a79ff77da317bbe6fa528
- https://github.com/liferay/liferay-portal/commit/d9108a12269e6b27689b2fd06f66fb881c8ec894
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-3526
