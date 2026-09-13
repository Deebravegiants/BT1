# [H] Vault's Google Cloud Secrets Engine Removed Existing IAM Conditions When Creating / Updating Rolesets

## Summary
Severity: High
Advisory: BIT-vault-2023-5077
Aliases: CVE-2023-5077, GHSA-86c6-3g63-5w64, GO-2023-2088
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2023-5077
Type: osv

## Affected
- Bitnami: `vault` — affected >=0.10.0 <1.13.0

## Details
The Vault and Vault Enterprise ("Vault") Google Cloud secrets engine did not preserve existing Google Cloud IAM Conditions upon creating or updating rolesets. Fixed in Vault 1.13.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2023-30-vault-s-google-cloud-secrets-engine-removed-existing-iam-conditions-when-creating-updating-rolesets/58654
- https://nvd.nist.gov/vuln/detail/CVE-2023-5077
