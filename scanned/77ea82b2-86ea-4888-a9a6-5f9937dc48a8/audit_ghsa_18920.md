# [H] expr-eval vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-8gw3-rxh4-v6jx
CVE: CVE-2025-13204
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-8gw3-rxh4-v6jx
Type: github-advisory

## Affected
- npm: `expr-eval` — affected >=0
- npm: `expr-eval-fork` — affected >=0 <2.0.2

## Details
npm package `expr-eval` is vulnerable to Prototype Pollution. An attacker with access to express eval interface can use JavaScript prototype-based inheritance model to achieve arbitrary code execution. The npm expr-eval-fork package resolves this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13204
- https://github.com/silentmatt/expr-eval/pull/252/files
- https://github.com/jorenbroekema/expr-eval/commit/6c475a118643ae0efe012de283e932fb8b74324b
- https://github.com/silentmatt/expr-eval/commit/6e889e0e75c50ac37d70c35388602025650e0c50
- https://github.com/SECCON/SECCON2022_final_CTF/blob/main/jeopardy/web/babybox/solver/solver.py
- https://github.com/jorenbroekema/expr-eval
- https://github.com/silentmatt/expr-eval
- https://github.com/vladko312/extras/blob/f549d505af300fd74a01b46fab2102990ff1c14d/expr-eval.py
- https://www.huntr.dev/bounties/1-npm-expr-eval
- https://www.npmjs.com/package/expr-eval-fork
