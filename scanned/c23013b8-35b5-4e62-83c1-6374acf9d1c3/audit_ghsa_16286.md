# [C] Liferay Portal has a Stored XSS with Blog entries (Insecure defaults)

## Summary
Severity: Critical
Advisory: GHSA-vvpf-53qx-cxhh
CVE: CVE-2024-25610
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-vvpf-53qx-cxhh
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.4.3.13
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u9
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp19
- Maven: `com.liferay.portal:com.liferay.portal.web` — affected >=0 <5.0.96

## Details
In Liferay Portal 7.2.0 through 7.4.3.12, and older unsupported versions, and Liferay DXP 7.4 before update 9, 7.3 before update 4, 7.2 before fix pack 19, and older unsupported versions, the default configuration does not sanitize blog entries of JavaScript, which allows remote authenticated users to inject arbitrary web script or HTML (XSS) via a crafted payload injected into a blog entry’s content text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25610
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25610
