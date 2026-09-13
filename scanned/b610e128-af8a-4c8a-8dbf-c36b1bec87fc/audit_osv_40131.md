# [H] pnpm: Transitive dependency alias path traversal allows project path override via symlink replacement

## Summary
Severity: High
Advisory: CVE-2026-50016
Aliases: GHSA-hwx4-2j3j-g496
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-50016
Type: osv

## Details
pnpm is a package manager. Prior to 10.34.0 and 11.4.0, pnpm allows a transitive dependency alias from registry package metadata to contain path traversal segments. During install, pnpm later uses that alias as a filesystem path when linking dependency nodes. As a result, a registry package can cause `pnpm install --ignore-scripts` to replace paths in the current project with symlinks to attacker-controlled dependency package directories. This vulnerability is fixed in 10.34.0 and 11.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50016.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-hwx4-2j3j-g496
- https://nvd.nist.gov/vuln/detail/CVE-2026-50016
