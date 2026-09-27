# [M] Liferay Portal and DXP do not check permissions of images in a blog entry

## Summary
Severity: Medium
Advisory: GHSA-xf7m-v66q-76w8
CVE: CVE-2025-62275
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-01
Source: https://github.com/advisories/GHSA-xf7m-v66q-76w8
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.blogs.item.selector.web` — affected >=0 <6.0.19

## Details
Blogs in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions does not check permission of images in a blog entry, which allows remote attackers to view the images in a blog entry via crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62275
- https://github.com/liferay/liferay-portal/commit/9856c55bcbb3b8ce1276117709b9c0082a19c62c
- https://github.com/liferay/liferay-portal/commit/e0ae29cfdb8d10a6fddc56d04ca3ae88c3fbc7f3
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17948
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62275
