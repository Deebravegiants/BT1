# [C] Liferay Portal XSS with `p_l_back_url_title` on edit content page

## Summary
Severity: Critical
Advisory: GHSA-v32m-pf9q-p3xg
CVE: CVE-2023-47797
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-v32m-pf9q-p3xg
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.94 <7.4.3.96

## Details
Reflected cross-site scripting (XSS) vulnerability on a content page’s edit page in Liferay Portal 7.4.3.94 through 7.4.3.95 allows remote attackers to inject arbitrary web script or HTML via the `p_l_back_url_title` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47797
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-47797
