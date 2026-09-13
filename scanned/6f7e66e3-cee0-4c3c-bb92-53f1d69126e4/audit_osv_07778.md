# [M] BIT-vault-2022-25243

## Summary
Severity: Medium
Advisory: BIT-vault-2022-25243
Aliases: CVE-2022-25243
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2022-25243
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.9.0 <1.9.4

## Details
"Vault and Vault Enterprise 1.8.0 through 1.8.8, and 1.9.3 allowed the PKI secrets engine under certain configurations to issue wildcard certificates to authorized users for a specified domain, even if the PKI role policy attribute allow_subdomains is set to false. Fixed in Vault Enterprise 1.8.9 and 1.9.4.

## References
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-09-vault-pki-secrets-engine-policy-results-in-incorrect-wildcard-certificate-issuance/36600
- https://security.gentoo.org/glsa/202207-01
- https://nvd.nist.gov/vuln/detail/CVE-2022-25243
