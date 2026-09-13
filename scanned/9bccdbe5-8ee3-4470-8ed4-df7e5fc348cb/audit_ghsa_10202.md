# [H] mathjs Allows Improperly Controlled Modification of Dynamically-Determined Object Attributes

## Summary
Severity: High
Advisory: GHSA-jvff-x2qm-6286
CVE: CVE-2026-41139
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-jvff-x2qm-6286
Type: github-advisory

## Affected
- npm: `mathjs` — affected >=13.1.0 <15.2.0

## Details
### Impact
This security vulnerability allowed executing arbitrary JavaScript via the expression parser of mathjs. You can be affected when you have an application where users can evaluate arbitrary expressions using the mathjs expression parser.

### Patches
The issue was introduced in mathjs `v13.1.0`, and patched in mathjs `v15.2.0`.

### Workarounds
There is no workaround without upgrading to `v15.2.0`.

### References
You can find out more via the commit fixing this issue: https://github.com/josdejong/mathjs/commit/24d5ee7e25e85d49619b09122f055db4139bc057 (part of PR https://github.com/josdejong/mathjs/pull/3656).

## References
- https://github.com/josdejong/mathjs/security/advisories/GHSA-5v89-rwgr-qj6g
- https://github.com/josdejong/mathjs/security/advisories/GHSA-jvff-x2qm-6286
- https://nvd.nist.gov/vuln/detail/CVE-2026-41139
- https://github.com/josdejong/mathjs/pull/3656
- https://github.com/josdejong/mathjs/commit/0aee2f61866e35ffa0aef915221cdf6b026ffdd4
- https://github.com/josdejong/mathjs/commit/bcf0da46f0b8577ec03c9ecd7bff8b5c2543a611
- https://github.com/josdejong/mathjs
- https://github.com/josdejong/mathjs/releases/tag/v15.2.0
