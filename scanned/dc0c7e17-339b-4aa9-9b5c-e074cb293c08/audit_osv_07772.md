# [H] BIT-vault-2021-27400

## Summary
Severity: High
Advisory: BIT-vault-2021-27400
Aliases: CVE-2021-27400
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2021-27400
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.7.0 <1.7.1

## Details
HashiCorp Vault and Vault Enterprise Cassandra integrations (storage backend and database secrets engine plugin) did not validate TLS certificates when connecting to Cassandra clusters. Fixed in 1.6.4 and 1.7.1

## References
- https://discuss.hashicorp.com/t/hcsec-2021-10-vault-s-cassandra-integrations-did-not-validate-tls-certificates/23463
- https://nvd.nist.gov/vuln/detail/CVE-2021-27400
