# [H] Trilium unauthenticated share-search discloses password-protected and hidden shared notes

## Summary
Severity: High
Advisory: CVE-2026-77438
Aliases: GHSA-6rxv-6w3q-7mv9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-77438
Type: osv

## Details
Trilium is an open-source hierarchical note-taking application. In versions up to and including 0.103.0, the public share-search endpoint does not enforce the per-note shareCredentials and shareHiddenFromTree controls, allowing an unauthenticated visitor to read the titles, tree paths, and content of protected shared notes. The endpoint authorizes only the ancestor note supplied in the request and then runs a full-text search across the entire published subtree, returning each matching note's title, share identifier, and hierarchical path without re-checking whether that individual note requires a share password or is hidden from the navigation tree. Because the search matches note content, an attacker can enumerate protected notes and use the endpoint as a boolean oracle that confirms arbitrary substrings, recovering the full contents of notes that should be gated behind a password. This issue is fixed in version 0.104.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77438.json
- https://github.com/TriliumNext/Trilium/security/advisories/GHSA-6rxv-6w3q-7mv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-77438
- https://github.com/TriliumNext/Trilium/commit/49fc7b67d9d49f01833e1ad9712ec83b079f98d2
