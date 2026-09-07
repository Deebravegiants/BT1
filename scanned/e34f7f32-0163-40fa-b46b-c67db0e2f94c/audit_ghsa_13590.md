# [M] ConcreteCMS vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-wrp2-6v6j-hfmg
CVE: CVE-2023-44763
CWE: CWE-434, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-wrp2-6v6j-hfmg
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0

## Details
Concrete CMS v9.2.1 is affected by Arbitrary File Upload vulnerability via the Thumbnail file upload, which allows Cross-Site Scripting (XSS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44763
- https://github.com/concretecms/concretecms
- https://github.com/sromanhu/ConcreteCMS-Arbitrary-file-upload-Thumbnail
- https://web.archive.org/web/20231026034159/https://documentation.concretecms.org/user-guide/editors-reference/dashboard/system-and-maintenance/files/allowed-file-types
- https://www.concretecms.org/about/project-news/security/security-advisory-2023-10-25-concrete-cms-rejects-cve-2023-44763
