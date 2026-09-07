# [M] NotrinosERP Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hrx5-cv4v-4c44
CVE: CVE-2022-2871
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-hrx5-cv4v-4c44
Type: github-advisory

## Affected
- Packagist: `notrinos/notrinos-erp` — affected >=0

## Details
NotrinosERP version 0.7 and prior is vulnerable to stored cross-site scripting. A fix is available on the `master` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2871
- https://github.com/notrinos/notrinoserp/commit/0362778f4f678156c22a009094225823df8a4760
- https://github.com/notrinos/notrinoserp
- https://huntr.dev/bounties/61126c07-22ac-4961-a198-1aa33060b373
