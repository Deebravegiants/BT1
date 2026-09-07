# [M] Hashicorp Vault has Incorrect Validation for Non-CA Certificates

## Summary
Severity: Medium
Advisory: GHSA-6c5r-4wfc-3mcx
CVE: CVE-2025-6037
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-6c5r-4wfc-3mcx
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.20.1

## Details
Vault and Vault Enterprise (“Vault”) TLS certificate auth method did not correctly validate client certificates when configured with a non-CA certificate as [+trusted certificate+|https://developer.hashicorp.com/vault/api-docs/auth/cert#certificate]. In this configuration, an attacker may be able to craft a malicious certificate that could be used to impersonate another user. Fixed in Vault Community Edition 1.20.1 and Vault Enterprise 1.20.1, 1.19.7, 1.18.12, and 1.16.23.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6037
- https://discuss.hashicorp.com/t/hcsec-2025-18-vault-certificate-auth-method-did-not-validate-common-name-for-non-ca-certificates/76037
- https://github.com/hashicorp/vault
