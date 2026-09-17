# [M] Vault Enterprise Namespace Creation May Lead to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-vault-2023-3774
Aliases: CVE-2023-3774
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2023-3774
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.14.0 <1.14.1

## Details
An unhandled error in Vault Enterprise's namespace creation may cause the Vault process to crash, potentially resulting in denial of service. Fixed in 1.14.1, 1.13.5, and 1.12.9.

## References
- https://discuss.hashicorp.com/t/hcsec-2023-23-vault-enterprise-namespace-creation-may-lead-to-denial-of-service/56617
- https://nvd.nist.gov/vuln/detail/CVE-2023-3774
