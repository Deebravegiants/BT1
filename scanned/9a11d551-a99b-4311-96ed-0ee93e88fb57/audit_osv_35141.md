# [H] Trilium Notes has a Timing Attack Vulnerability in /api/login/sync

## Summary
Severity: High
Advisory: CVE-2025-68621
Aliases: GHSA-hxf6-58cx-qq3x
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2025-68621
Type: osv

## Details
Trilium Notes is an open-source, cross-platform hierarchical note taking application with focus on building large personal knowledge bases.  Prior to 0.101.0, a critical timing attack vulnerability in Trilium's sync authentication endpoint allows unauthenticated remote attackers to recover HMAC authentication hashes byte-by-byte through statistical timing analysis. This enables complete authentication bypass without password knowledge, granting full read/write access to victim's knowledge base. This vulnerability is fixed in 0.101.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68621.json
- https://github.com/TriliumNext/Trilium/security/advisories/GHSA-hxf6-58cx-qq3x
- https://nvd.nist.gov/vuln/detail/CVE-2025-68621
- https://github.com/TriliumNext/Trilium/pull/8129
