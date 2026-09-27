# [H] Vault Incorrectly Validated JSON Web Tokens (JWT) Audience Claims

## Summary
Severity: High
Advisory: BIT-vault-2024-5798
Aliases: CVE-2024-5798, GHSA-32cj-5wx4-gq8p, GO-2024-2921
Ecosystem: Bitnami
Published: 2024-06-17
Source: https://osv.dev/vulnerability/BIT-vault-2024-5798
Type: osv

## Affected
- Bitnami: `vault` — affected >=0.11.0 <1.16.2

## Details
Vault and Vault Enterprise did not properly validate the JSON Web Token (JWT) role-bound audience claim when using the Vault JWT auth method. This may have resulted in Vault validating a JWT the audience and role-bound claims do not match, allowing an invalid login to succeed when it should have been rejected.

This vulnerability, CVE-2024-5798, was fixed in Vault and Vault Enterprise 1.17.0, 1.16.3, and 1.15.9

## References
- https://discuss.hashicorp.com/t/hcsec-2024-11-vault-incorrectly-validated-json-web-tokens-jwt-audience-claims/67770
- https://nvd.nist.gov/vuln/detail/CVE-2024-5798
