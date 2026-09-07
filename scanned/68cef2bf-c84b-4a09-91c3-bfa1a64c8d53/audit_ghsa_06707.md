# [M] @fastify/static vulnerable to Authorization Bypass via Non-Canonical URL Paths

## Summary
Severity: Medium
Advisory: GHSA-8pvw-jcv7-9cmj
CVE: CVE-2026-7120
CWE: CWE-180
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-8pvw-jcv7-9cmj
Type: github-advisory

## Affected
- npm: `@fastify/static` — affected >=0 <10.1.2

## Details
### Impact

`@fastify/static` evaluates the `allowedPath` callback before normalizing dot segments and duplicate slashes in the pathname used for file resolution. Non-canonical pathnames such as `//file`, `/./file`, or `/public/../private/file` bypass `allowedPath` filtering while resolving to the intended file on disk.

Applications that use `allowedPath` as a security boundary to restrict access to specific static files or path subtrees may unintentionally expose files that were intended to be denied.

### Patches

Upgrade to `@fastify/static` >= 10.1.2.

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/fastify/fastify-static/security/advisories/GHSA-8pvw-jcv7-9cmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-7120
- https://github.com/fastify/fastify-static/commit/878c72e920fabacf7e37739bf78057044717bf63
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-static
- https://github.com/fastify/fastify-static/releases/tag/v10.1.2
