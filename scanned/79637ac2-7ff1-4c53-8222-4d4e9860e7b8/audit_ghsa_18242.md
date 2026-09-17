# [M] Liferay Portal Vulnerable to IDOR via audit events

## Summary
Severity: Medium
Advisory: GHSA-pw86-qvx9-34r7
CVE: CVE-2025-43827
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-pw86-qvx9-34r7
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.security.audit.web` — affected >=5.0.1 <5.0.33
- Maven: `com.liferay:com.liferay.portal.security.audit.storage.service` — affected >=6.0.4 <6.0.41

## Details
Insecure Direct Object Reference (IDOR) vulnerability with audit events in Liferay Portal 7.4.0 through 7.4.3.117, and older unsupported versions, and Liferay DXP 2024.Q1.1 through 2024.Q1.5, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions allows remote authenticated users to from one virtual instance to view the audit events from a different virtual instance via the `_com_liferay_portal_security_audit_web_portlet_AuditPortlet_auditEventId` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43827
- https://github.com/liferay/liferay-portal/commit/a14427e2338477001f86a9e65fdddb843c319818
- https://github.com/liferay/liferay-portal/commit/d85c2f24397dcb7d9e51e7bd292dd29268efb132
- https://github.com/liferay/liferay-portal/commit/f99602a23ce1b3aa12b2625441cfaa17bfbd22b6
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17938
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43827
