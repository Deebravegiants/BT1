# [H] HashiCorp Vault Community Edition Denial of Service Though Complex JSON Payloads

## Summary
Severity: High
Advisory: GHSA-8f82-53h8-2p34
CVE: CVE-2025-6203
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-8f82-53h8-2p34
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0 <1.20.3

## Details
A malicious user may submit a specially-crafted complex payload that otherwise meets the default request size limit which results in excessive memory and CPU consumption of Vault. This may lead to a timeout in Vault’s auditing subroutine, potentially resulting in the Vault server to become unresponsive. This vulnerability, CVE-2025-6203, is fixed in Vault Community Edition 1.20.3 and Vault Enterprise 1.20.3, 1.19.9, 1.18.14, and 1.16.25.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6203
- https://github.com/hashicorp/vault/commit/eedc2b7426f30e57e306229ce697ce81e203ab89
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2025-24-vault-denial-of-service-though-complex-json-payloads/76393
- https://github.com/hashicorp/vault
