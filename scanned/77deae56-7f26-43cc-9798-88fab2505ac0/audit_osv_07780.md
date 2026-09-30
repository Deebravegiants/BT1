# [C] BIT-vault-2022-36129

## Summary
Severity: Critical
Advisory: BIT-vault-2022-36129
Aliases: CVE-2022-36129
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2022-36129
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.11.0 <1.11.1

## Details
HashiCorp Vault Enterprise 1.7.0 through 1.9.7, 1.10.4, and 1.11.0 clusters using Integrated Storage expose an unauthenticated API endpoint that could be abused to override the voter status of a node within a Vault HA cluster, introducing potential for future data loss or catastrophic failure. Fixed in Vault Enterprise 1.9.8, 1.10.5, and 1.11.1.

## References
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-15-vault-enterprise-does-not-verify-existing-voter-status-when-joining-an-integrated-storage-ha-node/42420
- https://security.netapp.com/advisory/ntap-20220901-0011/
- https://nvd.nist.gov/vuln/detail/CVE-2022-36129
