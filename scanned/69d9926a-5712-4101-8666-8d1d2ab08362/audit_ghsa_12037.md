# [M] Parse Server: `PagesRouter` path traversal allows reading files outside configured pages directory

## Summary
Severity: Medium
Advisory: GHSA-hm3f-q6rw-m6wh
CVE: CVE-2026-30848
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-hm3f-q6rw-m6wh
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.6.8
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.0-alpha.8

## Details
### Impact

The `PagesRouter` static file serving route is vulnerable to a path traversal attack that allows unauthenticated reading of files outside the configured `pagesPath` directory. The boundary check uses a string prefix comparison without enforcing a directory separator boundary. An attacker can use path traversal sequences to access files in sibling directories whose names share the same prefix as the pages directory (e.g. `pages-secret` starts with `pages`).

This affects any Parse Server deployment with the `pages` feature enabled (`pages.enableRouter: true`). Exploitation requires a sibling directory of `pagesPath` whose name begins with the same string as the pages directory name.

### Patches

The fix enforces a path separator boundary in the check, ensuring resolved paths must be strictly inside the `pagesPath` directory.

### Workarounds

Ensure the `pagesPath` directory has no sibling directories whose names begin with the same prefix. For example, if `pagesPath` is `/srv/pages`, ensure no directory like `/srv/pages-backup` or `/srv/pages_old` exists alongside it.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-hm3f-q6rw-m6wh
- Fix for Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.8
- Fix for Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.8

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-hm3f-q6rw-m6wh
- https://nvd.nist.gov/vuln/detail/CVE-2026-30848
- https://github.com/parse-community/parse-server
