# [M] Gleez CMS Stored XSS

## Summary
Severity: Medium
Advisory: GHSA-m2r2-qc49-gqw4
CVE: CVE-2018-7035
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m2r2-qc49-gqw4
Type: github-advisory

## Affected
- Packagist: `gleez/cms` — affected >=0
- Packagist: `gleez/cms` — affected 2.0.0

## Details
Cross-site scripting (XSS) vulnerability in Gleez CMS 1.2.0 and 2.0 might allow remote attackers (users) to inject JavaScript via HTML content in an editor, which will result in Stored XSS when an Administrator tries to edit the same content, as demonstrated by use of the source editor for HTML mode in an Add Blog action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7035
- https://github.com/gleez/cms/issues/794
- https://github.com/gleez/cms/issues/796
- https://github.com/gleez/cms/commit/d4ad1844e9fe6e2b9b92dfb351fb7e01047f9565
- https://github.com/gleez/cms
