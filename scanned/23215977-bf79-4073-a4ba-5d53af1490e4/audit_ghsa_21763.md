# [M] Path traversal in pimcore

## Summary
Severity: Medium
Advisory: GHSA-gjq4-69wj-p6pr
CVE: CVE-2022-0665
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-02-23
Source: https://github.com/advisories/GHSA-gjq4-69wj-p6pr
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.3.2

## Details
The application doesn't perform a check/filter against the value of "importFile" parameter at endpoint "/admin/translation/import". After the API is executed, PHP unlink function will proceed to delete the file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0665
- https://github.com/pimcore/pimcore/commit/28945649a6234ccaa8c94c6cd83d1954603baf3e
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/423df64d-c591-4ad9-bf1c-411bcbc06ba3
