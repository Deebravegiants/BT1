# [M] BIT-vault-2022-25244

## Summary
Severity: Medium
Advisory: BIT-vault-2022-25244
Aliases: CVE-2022-25244
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2022-25244
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.9.0 <1.9.4

## Details
Vault Enterprise clusters using the tokenization transform feature can expose the tokenization key through the tokenization key configuration endpoint to authorized operators with `read` permissions on this endpoint. Fixed in Vault Enterprise 1.9.4, 1.8.9 and 1.7.10.

## References
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-08-vault-enterprise-s-tokenization-transform-configuration-endpoint-may-expose-transform-key/36599
- https://nvd.nist.gov/vuln/detail/CVE-2022-25244
