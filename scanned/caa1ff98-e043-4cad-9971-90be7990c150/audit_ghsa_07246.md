# [H] Prompty: Arbitrary code execution via JavaScript frontmatter in TypeScript loader

## Summary
Severity: High
Advisory: GHSA-c4gh-rv8h-q9vw
CVE: CVE-2026-53597
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-c4gh-rv8h-q9vw
Type: github-advisory

## Affected
- npm: `@prompty/core` — affected >=2.0.0-alpha.1 <2.0.0-beta.3

## Details
## Summary
The TypeScript Prompty loader used `gray-matter` without overriding executable frontmatter engines. `gray-matter` supports JavaScript frontmatter blocks such as `---js` and evaluates them while parsing. An attacker-controlled `.prompty` file could therefore execute arbitrary JavaScript during prompt loading.

## Affected package
- npm `@prompty/core` v2 prerelease line: `>= 2.0.0-alpha.1 < 2.0.0-beta.3`
- Fixed in `@prompty/core@2.0.0-beta.3`

The legacy v1 JavaScript runtime had a historical hardening change for this issue. During the v2 TypeScript runtime rebuild, the loader again called `gray-matter` directly and the vulnerable behavior was present in the v2 prerelease packages until `2.0.0-beta.3`.

## Impact
Applications that load untrusted `.prompty` files, user-provided prompt paths, or prompt bundles from less-trusted locations could execute arbitrary JavaScript in the host Node.js process during frontmatter parsing.

## Remediation
Upgrade `@prompty/core` to `2.0.0-beta.3` or later.

The fix explicitly overrides the `js` and `javascript` gray-matter engines and rejects JavaScript frontmatter in `.prompty` files. Prompty frontmatter is YAML-only; executable frontmatter is unsupported. A regression test now verifies that `---js` frontmatter is rejected and not evaluated.

## Fix details
Fixed by commit `c27402da2487075be577f06aa79df627fb9d6853` and released via `typescript/2.0.0-beta.3`.

## References
- https://github.com/microsoft/prompty/security/advisories/GHSA-c4gh-rv8h-q9vw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53597
- https://github.com/microsoft/prompty/commit/c27402da2487075be577f06aa79df627fb9d6853
- https://github.com/microsoft/prompty
