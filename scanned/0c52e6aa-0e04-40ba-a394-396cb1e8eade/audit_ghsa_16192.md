# [M] Liferay Portal vulnerable to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-29xx-fhff-36m7
CVE: CVE-2024-26265
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-29xx-fhff-36m7
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.4.3.16

## Details
The Image Uploader module in Liferay Portal 7.2.0 through 7.4.3.15, and older unsupported versions, and Liferay DXP 7.4 before update 16, 7.3 before update 4, 7.2 before fix pack 19, and older unsupported versions relies on a request parameter to limit the size of files that can be uploaded, which allows remote authenticated users to upload arbitrarily large files to the system's temp folder by modifying the `maxFileSize` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26265
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-26265
