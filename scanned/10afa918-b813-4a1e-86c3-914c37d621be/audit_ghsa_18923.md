# [H] expr-eval does not restrict functions passed to the evaluate function

## Summary
Severity: High
Advisory: GHSA-jc85-fpwf-qm7x
CVE: CVE-2025-12735
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-jc85-fpwf-qm7x
Type: github-advisory

## Affected
- npm: `expr-eval` — affected >=0
- npm: `expr-eval-fork` — affected >=0 <3.0.1

## Details
The expr-eval library is a JavaScript expression parser and evaluator designed to safely evaluate mathematical expressions with user-defined variables. However, due to insufficient input validation, an attacker can pass a crafted variables object into the evaluate() function and trigger arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12735
- https://github.com/silentmatt/expr-eval/pull/288
- https://github.com/silentmatt/expr-eval/pull/289
- https://github.com/jorenbroekema/expr-eval/commit/1d71bb2ca8f98df8de00e9cc4de8fdd468a7ad43
- https://github.com/jorenbroekema/expr-eval
- https://github.com/jorenbroekema/expr-eval/blob/460b820ba01c5aca6c5d84a7d4f1fa5d1913c67b/test/security.js
- https://github.com/silentmatt/expr-eval
- https://kb.cert.org/vuls/id/263614
- https://www.kb.cert.org/vuls/id/263614
- https://www.npmjs.com/package/expr-eval
- https://www.npmjs.com/package/expr-eval-fork
