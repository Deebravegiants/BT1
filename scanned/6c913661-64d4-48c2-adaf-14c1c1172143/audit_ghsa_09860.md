# [H] Unsafe object property setter in mathjs

## Summary
Severity: High
Advisory: GHSA-29qv-4j9f-fjw5
CVE: CVE-2026-40897
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-29qv-4j9f-fjw5
Type: github-advisory

## Affected
- npm: `mathjs` — affected >=13.1.1 <15.2.0

## Details
### Impact
This security vulnerability allowed executing arbitrary JavaScript via the expression parser of mathjs. You can be affected when you have an application where users can evaluate arbitrary expressions using the mathjs expression parser.

### Patches
The issue was introduced in mathjs `v13.1.1`, and patched in mathjs `v15.2.0`.

### Workarounds
There is no workaround without upgrading to `v15.2.0`.

### References
You can find out more via the commit fixing this issue: https://github.com/josdejong/mathjs/commit/513ab2a0e01004af91b31aada68fae8a821326ad (part of PR https://github.com/josdejong/mathjs/pull/3656).

## References
- https://github.com/josdejong/mathjs/security/advisories/GHSA-29qv-4j9f-fjw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-40897
- https://github.com/josdejong/mathjs/pull/3656
- https://github.com/josdejong/mathjs/commit/513ab2a0e01004af91b31aada68fae8a821326ad
- https://github.com/josdejong/mathjs
