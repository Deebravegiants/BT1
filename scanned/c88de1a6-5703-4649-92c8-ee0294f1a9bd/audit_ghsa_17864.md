# [H] Hashicorp Vault has Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-6h4p-m86h-hhgh
CVE: CVE-2025-5999
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-6h4p-m86h-hhgh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.10.4 <1.20.0

## Details
A privileged Vault operator with write permissions to the root namespace’s identity endpoint could escalate their own or another user’s token privileges to Vault’s root policy. Fixed in Vault Community Edition 1.20.0 and Vault Enterprise 1.20.0, 1.19.6, 1.18.11 and 1.16.22.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5999
- https://discuss.hashicorp.com/t/hcsec-2025-13-vault-root-namespace-operator-may-elevate-token-privileges/76032
- https://github.com/hashicorp/vault
