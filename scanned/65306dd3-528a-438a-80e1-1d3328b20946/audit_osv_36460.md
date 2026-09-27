# [M] esm.sh has path traversal in `extractPackageTarball` that enables file writes from malicious packages

## Summary
Severity: Medium
Advisory: CVE-2026-23644
Aliases: GHSA-2657-3c98-63jq, GO-2026-4332
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-18
Source: https://osv.dev/vulnerability/CVE-2026-23644
Type: osv

## Details
esm.sh is a no-build content delivery network (CDN) for web development. Prior to Go pseeudoversion 0.0.0-20260116051925-c62ab83c589e, the software has a path traversal vulnerability due to an incomplete fix. `path.Clean` normalizes a path but does not prevent absolute paths in a malicious tar file. Commit https://github.com/esm-dev/esm.sh/commit/9d77b88c320733ff6689d938d85d246a3af9af16, corresponding to pseudoversion 0.0.0-20260116051925-c62ab83c589e, fixes this issue.

## References
- https://pkg.go.dev/vuln/GO-2025-4138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23644.json
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-2657-3c98-63jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-23644
- https://github.com/esm-dev/esm.sh/commit/9d77b88c320733ff6689d938d85d246a3af9af16
- https://github.com/esm-dev/esm.sh/commit/c62ab83c589e7b421a0e1376d2a00a4e48161093
