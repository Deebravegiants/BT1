# [M] Improper Removal of Sensitive Information Before Storage or Transfer in HashiCorp Vault

## Summary
Severity: Medium
Advisory: GHSA-6239-28c2-9mrm
CVE: CVE-2021-38554
CWE: CWE-212
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-6239-28c2-9mrm
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.6.6
- Go: `github.com/hashicorp/vault` — affected >=1.7.0 <1.7.4

## Details
HashiCorp Vault and Vault Enterprise’s UI erroneously cached and exposed user-viewed secrets between sessions in a single shared browser. Fixed in 1.8.0 and pending 1.7.4 / 1.6.6 releases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38554
- https://discuss.hashicorp.com/t/hcsec-2021-19-vault-s-ui-cached-user-viewed-secrets-between-shared-browser-sessions/28166
- https://github.com/hashicorp/vault
- https://github.com/hashicorp/vault/releases/tag/v1.6.6
- https://github.com/hashicorp/vault/releases/tag/v1.7.4
- https://security.gentoo.org/glsa/202207-01
