# [H] Oxia's TLS CA certificate chain validation fails with multi-certificate PEM bundles

## Summary
Severity: High
Advisory: GHSA-7jrq-q4pq-rhm6
CVE: CVE-2026-40944
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-7jrq-q4pq-rhm6
Type: github-advisory

## Affected
- Go: `github.com/oxia-db/oxia` — affected >=0 <0.16.2

## Details
### Summary
The `trustedCertPool()` function in the TLS configuration only parses the first PEM block from CA certificate files. When a CA bundle contains multiple certificates (e.g., intermediate + root CA), only the first certificate is loaded. This silently breaks certificate chain validation for mTLS.

### Impact
In deployments using mTLS with certificate chains (intermediate CA + root CA bundles), legitimate clients with properly chained certificates are rejected with `x509: certificate signed by unknown authority`. This degrades the security posture by making mTLS unusable with standard CA chain configurations, potentially forcing operators to disable client certificate verification.

All versions using TLS with `trustedCaFile` configuration are affected.

### Details
In `common/security/tls.go`, the `trustedCertPool()` method calls `pem.Decode()` only once, processing a single PEM block. The remaining bytes (containing additional certificates) are silently discarded. Additionally, the error return from `pem.Decode` is ignored, so a corrupted CA file results in an empty certificate pool without any error.

### Patches
Fixed by iterating over all PEM blocks in the file, parsing each CERTIFICATE block, and returning an error if no valid certificates are found.

### Workarounds
Use CA files containing only a single certificate (the direct issuer of client certificates, not a chain).

## References
- https://github.com/oxia-db/oxia/security/advisories/GHSA-7jrq-q4pq-rhm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40944
- https://github.com/oxia-db/oxia
