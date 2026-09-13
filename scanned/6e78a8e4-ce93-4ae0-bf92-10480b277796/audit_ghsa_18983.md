# [H] Vault’s Terraform Provider incorrectly set default deny_null_bind parameter for LDAP auth method to false by default

## Summary
Severity: High
Advisory: GHSA-gmm6-j2g5-r52m
CVE: CVE-2025-13357
CWE: CWE-1188
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-21
Source: https://github.com/advisories/GHSA-gmm6-j2g5-r52m
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/terraform-provider-vault` — affected >=0 <5.5.0

## Details
Vault’s Terraform Provider incorrectly set the default deny_null_bind parameter for the LDAP auth method to false by default, potentially resulting in an insecure configuration. If the underlying LDAP server allowed anonymous or unauthenticated binds, this could result in authentication bypass. This vulnerability, CVE-2025-13357, is fixed in Vault Terraform Provider v5.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13357
- https://github.com/hashicorp/terraform-provider-vault/pull/2622
- https://github.com/hashicorp/terraform-provider-vault/commit/882bc7f409acc99c872c345edd65159d9568589a
- https://discuss.hashicorp.com/t/hcsec-2025-33-vault-terraform-provider-applied-incorrect-defaults-for-ldap-auth-method/76822
- https://github.com/advisories/GHSA-gmm6-j2g5-r52m
- https://github.com/hashicorp/terraform-provider-vault
- https://github.com/hashicorp/terraform-provider-vault/releases/tag/v5.5.0
