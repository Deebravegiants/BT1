# [M] Hashicorp Vault may expose sensitive log information

## Summary
Severity: Medium
Advisory: GHSA-vgh3-mwxq-rcp8
CVE: CVE-2024-0831
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-vgh3-mwxq-rcp8
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.15.0 <1.15.5

## Details
Vault and Vault Enterprise (“Vault”) may expose sensitive information when enabling an audit device which specifies the `log_raw` option, which may log sensitive information to other audit devices, regardless of whether they are configured to use `log_raw`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0831
- https://github.com/hashicorp/vault/commit/2a72f2a8a5b57de88c22a2a94c4a5f08c6f3770b
- https://developer.hashicorp.com/vault/docs/upgrading/upgrade-to-1.15.x#audit-devices-could-log-raw-data-despite-configuration
- https://discuss.hashicorp.com/t/hcsec-2024-01-vault-may-expose-sensitive-information-when-configuring-an-audit-log-device/62311
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20240223-0005
