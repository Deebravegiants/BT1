# [M] BIT-vault-2021-45042

## Summary
Severity: Medium
Advisory: BIT-vault-2021-45042
Aliases: CVE-2021-45042
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2021-45042
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.9.0 <1.9.1

## Details
In HashiCorp Vault and Vault Enterprise before 1.7.7, 1.8.x before 1.8.6, and 1.9.x before 1.9.1, clusters using the Integrated Storage backend allowed an authenticated user (with write permissions to a kv secrets engine) to cause a panic and denial of service of the storage backend. The earliest affected version is 1.4.0.

## References
- https://discuss.hashicorp.com/t/hcsec2-21-33-vault-s-kv-secrets-engine-with-integrated-storage-exposed-to-authenticated-denial-of-service/33157
- https://security.gentoo.org/glsa/202207-01
- https://www.hashicorp.com/blog/category/vault
- https://nvd.nist.gov/vuln/detail/CVE-2021-45042
