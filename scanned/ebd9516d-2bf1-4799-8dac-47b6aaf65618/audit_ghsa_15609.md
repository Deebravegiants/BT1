# [H] Vault SSH Secrets Engine Configuration Did Not Restrict Valid Principals By Default

## Summary
Severity: High
Advisory: GHSA-jg74-mwgw-v6x3
CVE: CVE-2024-7594
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-26
Source: https://github.com/advisories/GHSA-jg74-mwgw-v6x3
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.7.7 <1.17.6
- Go: `github.com/openbao/openbao` — affected >=0.1.0
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20241003222810-d5b4e9224698

## Details
Vault’s SSH secrets engine did not require the valid_principals list to contain a value by default. If the valid_principals and default_user fields of the SSH secrets engine configuration are not set, an SSH certificate requested by an authorized user to Vault’s SSH secrets engine could be used to authenticate as any user on the host. Fixed in Vault Community Edition 1.17.6, and in Vault Enterprise 1.17.6, 1.16.10, and 1.15.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7594
- https://github.com/openbao/openbao/pull/561
- https://github.com/openbao/openbao/commit/d5b4e922469830ac335b21dc0e8f9878c501a884
- https://discuss.hashicorp.com/t/hcsec-2024-20-vault-ssh-secrets-engine-configuration-did-not-restrict-valid-principals-by-default/70251
- https://github.com/hashicorp/vault
- https://openbao.org/docs/release-notes/2-0-0/#202
- https://pkg.go.dev/vuln/GO-2024-3162
- https://security.netapp.com/advisory/ntap-20250110-0007
