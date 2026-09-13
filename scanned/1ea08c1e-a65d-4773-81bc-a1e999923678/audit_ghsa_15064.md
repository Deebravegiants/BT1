# [M] HashiCorp Vault Improper Privilege Management

## Summary
Severity: Medium
Advisory: GHSA-m979-w9wj-qfj9
CVE: CVE-2020-10660
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-m979-w9wj-qfj9
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.9.0 <1.3.4

## Details
HashiCorp Vault and Vault Enterprise versions 0.9.0 through 1.3.3 may, under certain circumstances, have an Entity's Group membership inadvertently include Groups the Entity no longer has permissions to. Fixed in 1.3.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10660
- https://github.com/hashicorp/vault/pull/8606
- https://github.com/hashicorp/vault/commit/18485ee9d4352ac8e8396c580b5941ccf8e5b31a
- https://github.com/hashicorp/vault
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#134-march-19th-2020
- https://www.hashicorp.com/blog/category/vault
