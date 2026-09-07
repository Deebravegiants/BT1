# [M] Mezzanine CMS has a Stored Cross-Site Scripting (XSS) vulnerability in the displayable_links_js function

## Summary
Severity: Medium
Advisory: GHSA-7pr5-w74r-jjj7
CVE: CVE-2025-6050
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-06-17
Source: https://github.com/advisories/GHSA-7pr5-w74r-jjj7
Type: github-advisory

## Affected
- PyPI: `Mezzanine` — affected >=0 <6.1.1

## Details
Mezzanine CMS, in versions prior to 6.1.1, contains a Stored Cross-Site Scripting (XSS) vulnerability in the admin interface. The vulnerability exists in the "displayable_links_js" function, which fails to properly sanitize blog post titles before including them in JSON responses served via "/admin/displayable_links.js". An authenticated admin user can create a blog post with a malicious JavaScript payload in the title field, then trick another admin user into clicking a direct link to the "/admin/displayable_links.js" endpoint, causing the malicious script to execute in their browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6050
- https://github.com/stephenmcd/mezzanine/commit/898630d8df48cf3ddb8b9942f59168b93216e3f8
- https://advisory.checkmarx.net/advisory/CVE-2025-6050
- https://github.com/advisories/GHSA-7pr5-w74r-jjj7
- https://github.com/pypa/advisory-database/tree/main/vulns/mezzanine/PYSEC-2025-236.yaml
- https://github.com/stephenmcd/mezzanine
- https://github.com/stephenmcd/mezzanine/discussions/2080
- https://https://github.com/stephenmcd/mezzanine/commit/898630d8df48cf3ddb8b9942f59168b93216e3f8
