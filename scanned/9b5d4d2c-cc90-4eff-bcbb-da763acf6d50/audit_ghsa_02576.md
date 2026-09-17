# [C] Prototype Pollution in immer

## Summary
Severity: Critical
Advisory: GHSA-33f9-j839-rf8h
CVE: CVE-2021-23436
CWE: CWE-1321, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-33f9-j839-rf8h
Type: github-advisory

## Affected
- npm: `immer` — affected >=7.0.0 <9.0.6

## Details
This affects the package immer before 9.0.6. A type confusion vulnerability can lead to a bypass of CVE-2020-28477 when the user-provided keys used in the path parameter are arrays. In particular, this bypass is possible because the condition `(p === "__proto__" || p === "constructor")` in `applyPatches_` returns false if `p` is `['__proto__']` (or `['constructor']`). The `===` operator (strict equality operator) returns false if the operands have different type.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23436
- https://github.com/immerjs/immer/commit/fa671e55ee9bd42ae08cc239102b665a23958237
- https://github.com/immerjs/immer
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1579266
- https://snyk.io/vuln/SNYK-JS-IMMER-1540542
