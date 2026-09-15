# [M] Hashicorp Vault has Lockout Feature Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-qgj7-fmq2-6cc4
CVE: CVE-2025-6004
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-qgj7-fmq2-6cc4
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.13.0 <1.20.1

## Details
Vault and Vault Enterprise’s (“Vault”) user lockout feature could be bypassed for Userpass and LDAP authentication methods. Fixed in Vault Community Edition 1.20.1 and Vault Enterprise 1.20.1, 1.19.7, 1.18.12, and 1.16.23.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6004
- https://discuss.hashicorp.com/t/hcsec-2025-16-vault-userpass-and-ldap-user-lockout-bypass/76035
- https://github.com/hashicorp/vault
