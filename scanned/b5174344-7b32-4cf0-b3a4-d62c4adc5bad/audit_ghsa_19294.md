# [M] Hashicorp Vault Community vulnerable to Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-f9ch-h8j7-8jwg
CVE: CVE-2025-3879
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-02
Source: https://github.com/advisories/GHSA-f9ch-h8j7-8jwg
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.10.0 <1.19.1

## Details
Vault Community, Vault Enterprise (“Vault”) Azure Auth method did not correctly validate the claims in the Azure-issued token, resulting in the potential bypass of the bound_locations parameter on login. Fixed in Vault Community Edition 1.19.1 and Vault Enterprise 1.19.1, 1.18.7, 1.17.14, 1.16.18.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3879
- https://discuss.hashicorp.com/t/hcsec-2025-07-vault-s-azure-authentication-method-bound-location-restriction-could-be-bypassed-on-login/74716
- https://github.com/hashicorp/vault
- https://pkg.go.dev/vuln/GO-2025-3662
