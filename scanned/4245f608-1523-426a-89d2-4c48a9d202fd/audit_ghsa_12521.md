# [M] Hashicorp Vault vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-gq98-53rq-qr5h
CVE: CVE-2023-2121
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-gq98-53rq-qr5h
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.11.11
- Go: `github.com/hashicorp/vault` — affected >=1.12.0 <1.12.7
- Go: `github.com/hashicorp/vault` — affected >=1.13.0 <1.13.3

## Details
Vault and Vault Enterprise's (Vault) key-value v2 (kv-v2) diff viewer allowed HTML injection into the Vault web UI through key values. This vulnerability, CVE-2023-2121, is fixed in Vault 1.14.0, 1.13.3, 1.12.7, and 1.11.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2121
- https://discuss.hashicorp.com/t/hcsec-2023-17-vault-s-kv-diff-viewer-allowed-html-injection/54814
- https://github.com/hashicorp/vault
