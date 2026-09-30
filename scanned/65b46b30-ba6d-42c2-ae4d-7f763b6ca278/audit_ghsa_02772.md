# [H] Improper Resource Shutdown or Release in HashiCorp Vault

## Summary
Severity: High
Advisory: GHSA-9vh5-r4qw-v3vv
CVE: CVE-2020-7220
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-07-28
Source: https://github.com/advisories/GHSA-9vh5-r4qw-v3vv
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.11.0 <1.3.2

## Details
HashiCorp Vault Enterprise 0.11.0 through 1.3.1 fails, in certain circumstances, to revoke dynamic secrets for a mount in a deleted namespace. Fixed in 1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7220
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#132-january-22nd-2020
- https://www.hashicorp.com/blog/category/vault
