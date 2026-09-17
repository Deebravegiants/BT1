# [H] HashiCorp Vault and Vault Enterprise's AWS Auth method may be susceptible to authentication bypass

## Summary
Severity: High
Advisory: GHSA-9g4h-h484-3578
CVE: CVE-2025-11621
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-9g4h-h484-3578
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.6.0 <1.21.0

## Details
Vault and Vault Enterprise's ("Vault") AWS Auth method may be susceptible to authentication bypass if the role of the configured bound_principal_iam is the same across AWS accounts, or uses a wildcard. This vulnerability is fixed in Vault Community Edition 1.21.0 and Vault Enterprise 1.21.0, 1.20.5, 1.19.11, and 1.16.27.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11621
- https://github.com/hashicorp/vault/commit/8d07273d14ae7f5a48cc96f66cc86615dea83390
- https://discuss.hashicorp.com/t/hcsec-2025-30-vault-aws-auth-method-authentication-bypass-through-mishandling-of-cache-entries/76709
- https://github.com/hashicorp/vault
