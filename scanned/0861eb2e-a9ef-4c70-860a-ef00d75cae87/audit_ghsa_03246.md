# [C] Improper Input Validation in HashiCorp Vault

## Summary
Severity: Critical
Advisory: GHSA-75pc-qvwc-jf3g
CVE: CVE-2020-12757
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-75pc-qvwc-jf3g
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault-plugin-secrets-gcp` — affected >=0 <0.6.2

## Details
HashiCorp Vault and Vault Enterprise 1.4.x before 1.4.2 in Go package github.com/hashicorp/vault-plugin-secrets-gcp/plugin has Incorrect Access Control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12757
- https://github.com/hashicorp/vault-plugin-secrets-gcp/pull/85
- https://github.com/hashicorp/vault-plugin-secrets-gcp/commit/e43d20870c50f7428dead1411debcec075b35fb4
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#142-may-21st-2020
- https://www.hashicorp.com/blog/category/vault
