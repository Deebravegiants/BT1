# [M] BIT-vault-2020-25816

## Summary
Severity: Medium
Advisory: BIT-vault-2020-25816
Aliases: CVE-2020-25816, GHSA-57gg-cj55-q5g2, GO-2024-2514
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2020-25816
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.5.0 <1.5.4

## Details
HashiCorp Vault and Vault Enterprise versions 1.0 and newer allowed leases created with a batch token to outlive their TTL because expiration time was not scheduled correctly. Fixed in 1.4.7 and 1.5.4.

## References
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#154
- https://www.hashicorp.com/blog/category/vault
- https://nvd.nist.gov/vuln/detail/CVE-2020-25816
