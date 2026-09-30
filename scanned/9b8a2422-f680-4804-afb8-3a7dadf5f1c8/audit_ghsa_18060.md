# [M] Hashicorp Vault has Login MFA Rate Limit Bypass Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v6r4-35f9-9rpw
CVE: CVE-2025-6015
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-v6r4-35f9-9rpw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.10.0 <1.20.1

## Details
Vault and Vault Enterprise’s (“Vault”) login MFA rate limits could be bypassed and TOTP tokens could be reused. Fixed in Vault Community Edition 1.20.1 and Vault Enterprise 1.20.1, 1.19.7, 1.18.12, and 1.16.23.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6015
- https://discuss.hashicorp.com/t/hcsec-2025-19-vault-login-mfa-bypass-of-rate-limiting-and-totp-token-reuse/76038
- https://github.com/hashicorp/vault
