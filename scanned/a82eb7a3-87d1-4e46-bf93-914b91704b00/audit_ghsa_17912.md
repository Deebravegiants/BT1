# [M] HashiCorp Vault ldap auth method may not have correctly enforced MFA

## Summary
Severity: Medium
Advisory: GHSA-7rx2-769v-hrwf
CVE: CVE-2025-6013
CWE: CWE-156
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-06
Source: https://github.com/advisories/GHSA-7rx2-769v-hrwf
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.20.2

## Details
Vault and Vault Enterprise’s (“Vault”) ldap auth method may not have correctly enforced MFA if username_as_alias was set to true and a user had multiple CNs that are equal but with leading or trailing spaces. Fixed in Vault Community Edition 1.20.2 and Vault Enterprise 1.20.2, 1.19.8, 1.18.13, and 1.16.24.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6013
- https://discuss.hashicorp.com/t/hcsec-2025-20-vault-ldap-mfa-enforcement-bypass-when-using-username-as-alias/76092
- https://github.com/hashicorp/vault
