# [H] Memory exhaustion in HashiCorp Vault

## Summary
Severity: High
Advisory: GHSA-6p62-6cg9-f5f5
CVE: CVE-2023-6337
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-09
Source: https://github.com/advisories/GHSA-6p62-6cg9-f5f5
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.15.0 <1.15.4
- Go: `github.com/hashicorp/vault` — affected >=1.14.0 <1.14.8
- Go: `github.com/hashicorp/vault` — affected >=1.12.0 <1.13.12

## Details
HashiCorp Vault and Vault Enterprise 1.12.0 and newer are vulnerable to a denial of service through memory exhaustion of the host when handling large unauthenticated and authenticated HTTP requests from a client. Vault will attempt to map the request to memory, resulting in the exhaustion of available memory on the host, which may cause Vault to crash.

Fixed in Vault 1.15.4, 1.14.8, 1.13.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6337
- https://github.com/hashicorp/vault/pull/24354
- https://discuss.hashicorp.com/t/hcsec-2023-34-vault-vulnerable-to-denial-of-service-through-memory-exhaustion-when-handling-large-http-requests/60741
- https://github.com/hashicorp/vault
- https://security.netapp.com/advisory/ntap-20240112-0006
