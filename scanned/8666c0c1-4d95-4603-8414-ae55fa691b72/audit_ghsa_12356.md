# [H] Directory Traversal in evershop

## Summary
Severity: High
Advisory: GHSA-rwf3-w4jq-f4cm
CVE: CVE-2023-46496
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-rwf3-w4jq-f4cm
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.8

## Details
Directory Traversal vulnerability in EverShop NPM versions before v.1.0.0-rc.8 allows a remote attacker to obtain sensitive information via a crafted request to the DELETE function in api/files endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46496
- https://github.com/evershopcommerce/evershop/pull/338
- https://devhub.checkmarx.com/cve-details/CVE-2023-46496
- https://devhub.checkmarx.com/cve-details/Cx943be66a-54cc
- https://github.com/evershopcommerce/evershop
