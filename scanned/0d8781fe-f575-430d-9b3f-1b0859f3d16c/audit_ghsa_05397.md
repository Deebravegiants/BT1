# [M] @backstage/cli-common has a possible `resolveSafeChildPath` Symlink Chain Bypass

## Summary
Severity: Medium
Advisory: GHSA-2p49-45hj-7mc9
CVE: CVE-2026-24047
CWE: CWE-59, CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-2p49-45hj-7mc9
Type: github-advisory

## Affected
- npm: `@backstage/cli-common` — affected >=0 <0.1.17

## Details
### Impact

The `resolveSafeChildPath` utility function in `@backstage/backend-plugin-api`, which is used to prevent path traversal attacks, failed to properly validate symlink chains and dangling symlinks. An attacker could bypass the path validation by:

1. **Symlink chains**: Creating `link1 → link2 → /outside` where intermediate symlinks eventually resolve outside the allowed directory
2. **Dangling symlinks**: Creating symlinks pointing to non-existent paths outside the base directory, which would later be created during file operations

This function is used by Scaffolder actions and other backend components to ensure file operations stay within designated directories.

### Patches

This vulnerability is fixed in `@backstage/backend-plugin-api` version 0.1.17. Users should upgrade to this version or later.

### Workarounds

- Run Backstage in a containerised environment with limited filesystem access
- Restrict template creation to trusted users

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-2p49-45hj-7mc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24047
- https://github.com/backstage/backstage/commit/ae4dd5d1572a4f639e1a466fd982656b50f8e692
- https://github.com/backstage/backstage
