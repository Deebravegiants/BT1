# [H] @fastify/middie vulnerable to middleware bypass via deprecated ignoreDuplicateSlashes option

## Summary
Severity: High
Advisory: GHSA-v9ww-2j6r-98q6
CVE: CVE-2026-33804
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-v9ww-2j6r-98q6
Type: github-advisory

## Affected
- npm: `@fastify/middie` — affected >=0 <9.3.2

## Details
### Impact

`@fastify/middie` v9.3.1 and earlier does not read the deprecated (but still functional) top-level `ignoreDuplicateSlashes` option, only reading from `routerOptions`. This creates a normalization gap: Fastify's router normalizes duplicate slashes but middie does not, allowing middleware bypass via URLs with duplicate leading slashes (e.g., `//admin/secret`).

This only affects applications using the deprecated top-level configuration style (`fastify({ ignoreDuplicateSlashes: true })`). Applications using `routerOptions: { ignoreDuplicateSlashes: true }` are not affected.

This is distinct from [GHSA-8p85-9qpw-fwgw](https://github.com/fastify/middie/security/advisories/GHSA-8p85-9qpw-fwgw) (CVE-2026-2880), which was patched in v9.2.0.

### Patches

Upgrade to `@fastify/middie` >= 9.3.2.

### Workarounds

Migrate from deprecated top-level `ignoreDuplicateSlashes: true` to `routerOptions: { ignoreDuplicateSlashes: true }`.

## References
- https://github.com/fastify/middie/security/advisories/GHSA-v9ww-2j6r-98q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33804
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/middie
