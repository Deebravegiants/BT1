# [M] HashiCorp Vault and Vault Enterprise vulnerable to user enumeration

## Summary
Severity: Medium
Advisory: GHSA-9v3w-w2jh-4hff
CVE: CVE-2023-3462
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-9v3w-w2jh-4hff
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.13.5
- Go: `github.com/hashicorp/vault` — affected >=1.14.0 <1.14.1

## Details
HashiCorp's Vault and Vault Enterprise are vulnerable to user enumeration when using the LDAP auth method. An attacker may submit requests of existent and non-existent LDAP users and observe the response from Vault to check if the account is valid on the LDAP server. This vulnerability is fixed in Vault 1.14.1 and 1.13.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3462
- https://discuss.hashicorp.com/t/hcsec-2023-24-vaults-ldap-auth-method-allows-for-user-enumeration/56714
- https://github.com/hashicorp/vault
