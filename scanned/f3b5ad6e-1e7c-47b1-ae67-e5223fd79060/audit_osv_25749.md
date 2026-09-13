# [M] TaxonWorks SQL injection vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-43640
Aliases: GHSA-m9p2-jxr6-4p6c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-09-22
Source: https://osv.dev/vulnerability/CVE-2023-43640
Type: osv

## Details
TaxonWorks is a web-based workbench designed for taxonomists and biodiversity scientists. Prior to version 0.34.0, a SQL injection vulnerability was found in TaxonWorks that allows authenticated attackers to extract arbitrary data from the TaxonWorks database (including the users table). This issue may lead to information disclosure. Version 0.34.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43640.json
- https://github.com/SpeciesFileGroup/taxonworks/security/advisories/GHSA-m9p2-jxr6-4p6c
- https://nvd.nist.gov/vuln/detail/CVE-2023-43640
- https://github.com/SpeciesFileGroup/taxonworks/commit/a98f2dc610a541678e1e51af47659cd8b30179ae
