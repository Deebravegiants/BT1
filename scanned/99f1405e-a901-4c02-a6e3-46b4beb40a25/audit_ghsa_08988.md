# [H] @babel/plugin-transform-modules-systemjs generates arbitrary code when compiling malicious input

## Summary
Severity: High
Advisory: GHSA-fv7c-fp4j-7gwp
CVE: CVE-2026-44728
CWE: CWE-843, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-fv7c-fp4j-7gwp
Type: github-advisory

## Affected
- npm: `@babel/plugin-transform-modules-systemjs` — affected >=7.12.0 <7.29.4
- npm: `@babel/plugin-transform-modules-systemjs` — affected >=8.0.0-alpha.0 <8.0.0-alpha.13

## Details
### Impact

Using Babel to compile code that was specifically crafted by an attacker can cause Babel to generate output code that executes arbitrary code.

Known affected plugins are:
- `@babel/plugin-transform-modules-systemjs`
- `@babel/preset-env` when using the [`modules: "systemjs"` option](https://babel.dev/docs/babel-preset-env#modules), as it delegates to `@babel/plugin-transform-modules-systemjs`

No other plugins under the `@babel` namespace are impacted.

**Users that only compile trusted code are not impacted.**

### Patches

The vulnerability has been fixed in `@babel/plugin-transform-modules-systemjs@7.29.4`.

Babel also released `@babel/preset-env@7.29.5`, updating its `@babel/plugin-transform-modules-systemjs` dependency, to simplify forcing the update if you are using `@babel/preset-env` directly.

### Workarounds

- Pin `@babel/parser` to v7.11.5. The downgrade will completely disable string module name parsing, but it would also disable other new language features and the build pipeline may fail as a result. Only do so if you are working on a legacy codebase and can not upgrade `@babel/plugin-transform-modules-systemjs` to v7.29.4.
- Do not use the `modules: "systemjs"` option, migrate the codebase to native ES Modules or any other module formats.

### Credits
Babel thanks Daniel Cervera for reporting the vulnerability.

## References
- https://github.com/babel/babel/security/advisories/GHSA-fv7c-fp4j-7gwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44728
- https://github.com/babel/babel
