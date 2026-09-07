# [H] Incorrect TLS certificate auth method in Vault

## Summary
Severity: High
Advisory: GHSA-r3w7-mfpm-c2vw
CVE: CVE-2024-2048
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-r3w7-mfpm-c2vw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.15.0 <1.15.5
- Go: `github.com/hashicorp/vault` — affected >=0 <1.14.10

## Details
Vault and Vault Enterprise (“Vault”) TLS certificate auth method did not correctly validate client certificates when configured with a non-CA certificate as trusted certificate. In this configuration, an attacker may be able to craft a malicious certificate that could be used to bypass authentication. Fixed in Vault 1.15.5 and 1.14.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2048
- https://discuss.hashicorp.com/t/hcsec-2024-05-vault-cert-auth-method-did-not-correctly-validate-non-ca-certificates/63382
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20240524-0009
