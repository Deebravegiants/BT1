# [H] Liferay Portal Vulnerable to Denial of Service in Kaleo Forms Admin

## Summary
Severity: High
Advisory: GHSA-j4fw-4mhr-hc45
CVE: CVE-2025-43772
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-j4fw-4mhr-hc45
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.workflow.kaleo.forms.web` — affected >=0 <5.0.29

## Details
Kaleo Forms Admin in Liferay Portal 7.0.0 through 7.4.3.4, and Liferay DXP 7.4 GA, 7.3 GA through update 27, and older unsupported versions does not restrict the saving of request parameters in the portlet session, which allows remote attackers to consume system memory leading to denial-of-service (DoS) conditions via crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43772
- https://github.com/liferay/liferay-portal/commit/566ba7b48d6e8c62e5da71c34bb56b87183bf503
- https://github.com/liferay/liferay-portal/commit/5d62db9d01005fc148297dad37f84660cd8b4a2b
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17456
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43772
