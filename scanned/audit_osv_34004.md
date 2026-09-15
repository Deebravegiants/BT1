# [H] Trilium Notes is Vulnerable to Brute-force Protection Bypass via Initial Sync Seed Retrieval

## Summary
Severity: High
Advisory: CVE-2025-53544
Aliases: GHSA-hw5p-ff75-327r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-53544
Type: osv

## Details
Trilium Notes is an open-source, cross-platform hierarchical note taking application with focus on building large personal knowledge bases. In versions below 0.97.0, a brute-force protection bypass in the initial sync seed retrieval endpoint allows unauthenticated attackers to guess the login password without triggering rate limiting. Trilium is a single-user app without a username requirement, and brute-force protection bypass makes exploitation much more feasible. Multiple features provided by Trilium (e.g. MFA, share notes, custom request handler) indicate that Trilium can be exposed to the internet. This is fixed in version 0.97.0.

## References
- https://github.com/TriliumNext/Trilium/pull/6243/commits/04c8f8a1234e8c9f4a87da187180375227b21223
- https://github.com/TriliumNext/Trilium/releases/tag/v0.97.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53544.json
- https://github.com/TriliumNext/Trilium/security/advisories/GHSA-hw5p-ff75-327r
- https://nvd.nist.gov/vuln/detail/CVE-2025-53544
