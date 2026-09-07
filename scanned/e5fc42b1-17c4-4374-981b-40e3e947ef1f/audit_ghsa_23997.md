# [M] Liferay Portal Vulnerable to XSS in Profile Search Functionality

## Summary
Severity: Medium
Advisory: GHSA-hq29-vqg6-pjpw
CVE: CVE-2016-3670
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hq29-vqg6-pjpw
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.search.web` — affected >=0 <1.0.3

## Details
Cross-site scripting (XSS) vulnerability in users.jsp in the Profile Search functionality in Liferay Portal Search Web before 1.0.3 from Liferay (before 7.0.0 CE RC1) allows remote attackers to inject arbitrary web script or HTML via the FirstName field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3670
- https://github.com/liferay/liferay-portal/commit/b7ce087039f3b753f36f558df5faefac4ad4b160
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPS-62387
- https://labs.integrity.pt/advisories/cve-2016-3670
- https://www.exploit-db.com/exploits/39880
- http://packetstormsecurity.com/files/137279/Liferay-CE-Stored-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2016/Jun/5
- http://www.securitytracker.com/id/1036083
