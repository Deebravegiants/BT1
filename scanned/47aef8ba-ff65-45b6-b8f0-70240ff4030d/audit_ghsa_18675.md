# [H] Hashicorp Vault and Vault Enterprise vulnerable to a denial of service when processing JSON

## Summary
Severity: High
Advisory: GHSA-vp5w-xcfc-73wf
CVE: CVE-2025-12044
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-vp5w-xcfc-73wf
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.20.3 <1.21.0

## Details
Vault and Vault Enterprise ("Vault") are vulnerable to an unauthenticated denial of service when processing JSON payloads. This occurs due to a regression from a previous fix for [+HCSEC-2025-24+|https://discuss.hashicorp.com/t/hcsec-2025-24-vault-denial-of-service-though-complex-json-payloads/76393]  which allowed for processing JSON payloads before applying rate limits. This vulnerability, CVE-2025-12044, is fixed in Vault Community Edition 1.21.0 and Vault Enterprise 1.16.27, 1.19.11, 1.20.5, and 1.21.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12044
- https://github.com/hashicorp/vault/commit/b19e74c29a33ed2a99fc01626104db1a49345df3
- https://github.com/hashicorp/vault/commit/eedc2b7426f30e57e306229ce697ce81e203ab89
- https://discuss.hashicorp.com/t/hcsec-2025-31-vault-vulnerable-to-denial-of-service-due-to-rate-limit-regression/76710
- https://github.com/hashicorp/vault
