# [M] BIT-vault-2020-35453

## Summary
Severity: Medium
Advisory: BIT-vault-2020-35453
Aliases: CVE-2020-35453
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2020-35453
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.6.0 <1.6.1

## Details
HashiCorp Vault Enterprise’s Sentinel EGP policy feature incorrectly allowed requests to be processed in parent and sibling namespaces. Fixed in 1.5.6 and 1.6.1.

## References
- https://discuss.hashicorp.com/t/hcsec-2020-24-vault-enterprise-s-sentinel-egp-policies-may-impact-parent-or-sibling-namespaces/18983
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#161
- https://nvd.nist.gov/vuln/detail/CVE-2020-35453
