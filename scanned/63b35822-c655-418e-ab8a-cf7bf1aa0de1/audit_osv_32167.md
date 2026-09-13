# [H] BCryptGenerateSymmetricKey memory leak

## Summary
Severity: High
Advisory: CVE-2025-25199
Aliases: GHSA-29c6-3hcj-89cf, GO-2025-3461
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-25199
Type: osv

## Details
go-crypto-winnative Go crypto backend for Windows using Cryptography API: Next Generation (CNG). Prior to commit f49c8e1379ea4b147d5bff1b3be5b0ff45792e41, calls to `cng.TLS1PRF` don't release the key handle, producing a small memory leak every time. Commit f49c8e1379ea4b147d5bff1b3be5b0ff45792e41 contains a fix for the issue. The fix is included in versions 1.23.6-2 and 1.22.12-2 of the Microsoft build of go, as well as in the pseudoversion 0.0.0-20250211154640-f49c8e1379ea of the `github.com/microsoft/go-crypto-winnative` Go package.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25199.json
- https://github.com/microsoft/go-crypto-winnative/security/advisories/GHSA-29c6-3hcj-89cf
- https://nvd.nist.gov/vuln/detail/CVE-2025-25199
- https://github.com/microsoft/go-crypto-winnative/commit/f49c8e1379ea4b147d5bff1b3be5b0ff45792e41
