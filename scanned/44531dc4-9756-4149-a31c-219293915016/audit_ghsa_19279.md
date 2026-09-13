# [M] Hashicorp Vault Community vulnerable to Generation of Error Message Containing Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-gcqf-f89c-68hv
CVE: CVE-2025-4166
CWE: CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-02
Source: https://github.com/advisories/GHSA-gcqf-f89c-68hv
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.3.0 <1.19.3

## Details
Vault Community and Vault Enterprise Key/Value (kv) Version 2 plugin may unintentionally expose sensitive information in server and audit logs when users submit malformed payloads during secret creation or update operations via the Vault REST API. This vulnerability, identified as CVE-2025-4166, is fixed in Vault Community 1.19.3 and Vault Enterprise 1.19.3, 1.18.9, 1.17.16, 1.16.20.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4166
- https://discuss.hashicorp.com/t/hcsec-2025-09-vault-may-expose-sensitive-information-in-error-logs-when-processing-malformed-data-with-the-kv-v2-plugin
- https://github.com/hashicorp/vault
- https://pkg.go.dev/vuln/GO-2025-3663
