# [C] BIT-vault-2020-10661

## Summary
Severity: Critical
Advisory: BIT-vault-2020-10661
Aliases: CVE-2020-10661, GHSA-j6vv-vv26-rh7c, GO-2024-2485
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2020-10661
Type: osv

## Affected
- Bitnami: `vault` — affected >=0.11.0 <1.3.4

## Details
HashiCorp Vault and Vault Enterprise versions 0.11.0 through 1.3.3 may, under certain circumstances, have existing nested-path policies grant access to Namespaces created after-the-fact. Fixed in 1.3.4.

## References
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#134-march-19th-2020
- https://www.hashicorp.com/blog/category/vault/
- https://nvd.nist.gov/vuln/detail/CVE-2020-10661
