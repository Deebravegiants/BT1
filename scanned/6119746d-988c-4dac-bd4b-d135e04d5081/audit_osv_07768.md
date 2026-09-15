# [M] BIT-vault-2020-25594

## Summary
Severity: Medium
Advisory: BIT-vault-2020-25594
Aliases: CVE-2020-25594
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2020-25594
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.6.0 <1.6.2

## Details
HashiCorp Vault and Vault Enterprise allowed for enumeration of Secrets Engine mount paths via unauthenticated HTTP requests. Fixed in 1.6.2 & 1.5.7.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-03-vault-api-endpoint-allowed-enumeration-of-secrets-engine-mount-paths-without-authentication/20336
- https://security.gentoo.org/glsa/202207-01
- https://nvd.nist.gov/vuln/detail/CVE-2020-25594
