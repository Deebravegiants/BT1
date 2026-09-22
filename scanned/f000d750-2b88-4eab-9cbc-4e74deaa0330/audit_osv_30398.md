# [H] Craft has a Potential Remote Code Execution via missing path normalization & Twig SSTI

## Summary
Severity: High
Advisory: CVE-2024-52293
Aliases: GHSA-f3cw-hg6r-chfv
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/CVE-2024-52293
Type: osv

## Details
Craft is a content management system (CMS). Prior to 4.12.2 and 5.4.3, Craft is missing normalizePath in the function FileHelper::absolutePath could lead to Remote Code Execution on the server via twig SSTI. This is a sequel to CVE-2023-40035. This vulnerability is fixed in 4.12.2 and 5.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52293.json
- https://github.com/craftcms/cms/security/advisories/GHSA-f3cw-hg6r-chfv
- https://nvd.nist.gov/vuln/detail/CVE-2024-52293
- https://github.com/craftcms/cms/commit/123e48a696de1e2f63ab519d4730eb3b87beaa58
