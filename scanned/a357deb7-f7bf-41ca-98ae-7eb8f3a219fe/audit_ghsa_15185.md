# [M] Enumeration of users in HashiCorp Vault

## Summary
Severity: Medium
Advisory: GHSA-rpgp-9hmg-j25x
CVE: CVE-2020-35177
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N/E:U/RL:O/RC:R (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-rpgp-9hmg-j25x
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.5.0 <1.5.6
- Go: `github.com/hashicorp/vault` — affected >=1.6.0 <1.6.1

## Details
HashiCorp Vault and Vault Enterprise allowed the enumeration of users via the LDAP auth method. Fixed in 1.5.6 and 1.6.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35177
- https://github.com/hashicorp/vault/pull/10537
- https://discuss.hashicorp.com/t/hcsec-2020-25-vault-s-ldap-auth-method-allows-user-enumeration/18984
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#161
