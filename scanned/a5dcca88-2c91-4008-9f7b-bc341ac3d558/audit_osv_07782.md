# [M] Vault Enterprise's Sentinel RGP Policies Allowed For Cross-Namespace Denial of Service

## Summary
Severity: Medium
Advisory: BIT-vault-2023-3775
Aliases: CVE-2023-3775
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2023-3775
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.14.0 <1.14.4

## Details
A Vault Enterprise Sentinel Role Governing Policy created by an operator to restrict access to resources in one namespace can be applied to requests outside in another non-descendant namespace, potentially resulting in denial of service. Fixed in Vault Enterprise 1.15.0, 1.14.4, 1.13.8.

## References
- https://discuss.hashicorp.com/t/hcsec-2023-29-vault-enterprise-s-sentinel-rgp-policies-allowed-for-cross-namespace-denial-of-service/58653
- https://nvd.nist.gov/vuln/detail/CVE-2023-3775
