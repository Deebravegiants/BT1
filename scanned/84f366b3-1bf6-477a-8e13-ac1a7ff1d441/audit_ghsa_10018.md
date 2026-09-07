# [M] @fastify/static vulnerable to path traversal in directory listing

## Summary
Severity: Medium
Advisory: GHSA-pr96-94w5-mx2h
CVE: CVE-2026-6410
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-pr96-94w5-mx2h
Type: github-advisory

## Affected
- npm: `@fastify/static` — affected >=8.0.0 <9.1.1

## Details
### Impact

`@fastify/static` v9.1.0 and earlier serves directory listings outside the configured static root when the `list` option is enabled. A request such as `/public/../outside/` causes `dirList.path()` to resolve a directory outside the root via `path.join()` without a containment check.

A remote unauthenticated attacker can obtain directory listings for arbitrary directories accessible to the Node.js process, disclosing directory names and filenames that should not be exposed. File contents are not disclosed.

### Patches

Upgrade to `@fastify/static` >= 9.1.1.

### Workarounds

Disable directory listing by removing the `list` option from the plugin configuration.

## References
- https://github.com/fastify/fastify-static/security/advisories/GHSA-pr96-94w5-mx2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-6410
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-static
