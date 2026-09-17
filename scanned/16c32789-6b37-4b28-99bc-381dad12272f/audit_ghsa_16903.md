# [M] HashiCorpVault does not correctly validate OCSP responses

## Summary
Severity: Medium
Advisory: GHSA-j2rp-gmqv-frhv
CVE: CVE-2024-2660
CWE: CWE-636, CWE-703
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-j2rp-gmqv-frhv
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.16.0

## Details
Vault and Vault Enterprise TLS certificates auth method did not correctly validate OCSP responses when one or more OCSP sources were configured. Fixed in Vault 1.16.0 and Vault Enterprise 1.16.1, 1.15.7, and 1.14.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2660
- https://discuss.hashicorp.com/t/hcsec-2024-07-vault-tls-cert-auth-method-did-not-correctly-validate-ocsp-responses/64573
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20240524-0007
