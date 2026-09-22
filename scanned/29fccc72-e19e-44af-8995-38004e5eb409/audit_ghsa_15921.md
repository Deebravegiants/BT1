# [H] Vault Community Edition privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-rr8j-7w34-xp5j
CVE: CVE-2024-9180
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-rr8j-7w34-xp5j
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.18.0
- Go: `github.com/openbao/openbao` — affected >=0 <2.0.3

## Details
A privileged Vault operator with write permissions to the root namespace’s identity endpoint could escalate their privileges to Vault’s root policy. Fixed in Vault Community Edition 1.18.0 and Vault Enterprise 1.18.0, 1.17.7, 1.16.11, and 1.15.16

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9180
- https://discuss.hashicorp.com/t/hcsec-2024-21-vault-operators-in-root-namespace-may-elevate-their-privileges/70565
- https://github.com/hashicorp/vault
- https://openbao.org/docs/release-notes/2-0-0/#203
- https://pkg.go.dev/vuln/GO-2024-3191
