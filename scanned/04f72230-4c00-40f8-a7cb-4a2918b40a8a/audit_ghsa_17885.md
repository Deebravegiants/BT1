# [M] Hashicorp Vault's TOTP Secrets Engine Susceptible to Code Reuse 

## Summary
Severity: Medium
Advisory: GHSA-qv3p-fmv3-9hww
CVE: CVE-2025-6014
CWE: CWE-156
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-qv3p-fmv3-9hww
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.20.1

## Details
Vault and Vault Enterprise’s (“Vault”) TOTP Secrets Engine code validation endpoint is susceptible to code reuse within its validity period. Fixed in Vault Community Edition 1.20.1 and Vault Enterprise 1.20.1, 1.19.7, 1.18.12, and 1.16.23.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6014
- https://discuss.hashicorp.com/t/hcsec-2025-17-vault-totp-secrets-engine-code-reuse/76036
- https://github.com/hashicorp/vault
