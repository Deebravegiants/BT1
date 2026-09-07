# [M] In-memory stored Cross-site scripting (XSS) vulnerability in pineconesim

## Summary
Severity: Medium
Advisory: GHSA-fr62-mg2q-7wqv
CVE: CVE-2025-27155
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-04
Source: https://github.com/advisories/GHSA-fr62-mg2q-7wqv
Type: github-advisory

## Affected
- Go: `github.com/matrix-org/pinecone` — affected >=0

## Details
### Impact
The Pinecone Simulator (pineconesim) included in Pinecone up to commit https://github.com/matrix-org/pinecone/commit/ea4c33717fd74ef7d6f49490625a0fa10e3f5bbc is vulnerable to stored cross-site scripting. The payload storage is not permanent and will be wiped when restarting pineconsim.

### Patches
Commit https://github.com/matrix-org/pinecone/commit/218b2801995b174085cb1c8fafe2d3aa661f85bd contains the fixes.

### Workarounds
N/A

### For more information

If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/pinecone/security/advisories/GHSA-fr62-mg2q-7wqv
- https://nvd.nist.gov/vuln/detail/CVE-2025-27155
- https://github.com/matrix-org/pinecone/commit/218b2801995b174085cb1c8fafe2d3aa661f85bd
- https://github.com/matrix-org/pinecone
- https://pkg.go.dev/vuln/GO-2025-3500
