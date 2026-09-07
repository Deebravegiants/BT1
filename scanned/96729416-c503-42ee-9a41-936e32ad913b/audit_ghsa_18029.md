# [C] Hashicorp Vault has Code Execution Vulnerability via Plugin Configuration

## Summary
Severity: Critical
Advisory: GHSA-mr4h-qf9j-f665
CVE: CVE-2025-6000
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-mr4h-qf9j-f665
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.8.0 <1.20.1

## Details
A privileged Vault operator within the root namespace with write permission to {{sys/audit}} may obtain code execution on the underlying host if a plugin directory is set in Vault’s configuration. Fixed in Vault Community Edition 1.20.1 and Vault Enterprise 1.20.1, 1.19.7, 1.18.12, and 1.16.23.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6000
- https://discuss.hashicorp.com/t/hcsec-2025-14-privileged-vault-operator-may-execute-code-on-the-underlying-host/76033
- https://github.com/hashicorp/vault
