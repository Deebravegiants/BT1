# [C] Orval: Import-time RCE via query-parameter default -> zod module-level template literal

## Summary
Severity: Critical
Advisory: GHSA-p4cg-3328-rvfg
CVE: CVE-2026-72716
CWE: CWE-1336
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-p4cg-3328-rvfg
Type: github-advisory

## Affected
- npm: `orval` — affected >=0 <8.21.0

## Details
### Summary

Orval's zod schema generation emits the **query-parameter** `default` value as a module-level template literal
(`export const …Default = `<default>`;`) without escaping `${` or the backtick. A default of the form
`v${<code>}w` injects a live JavaScript expression evaluated when the generated zod schema module is
imported, executing attacker-controlled code at import — no request or function call needed. Verified
on Orval 8.19.0; survives default OpenAPI validation.

### Details

```ts
export const …Default = `v${globalThis.ORVPWN()}w`;   // ${...} = arbitrary JS expression, runs at import
```

Malicious input: a query parameter with a `default` of `v${<attacker JS>}w`. `${...}` permits any JS expression.

Note: this is one of several `default`-bearing positions that reach the same unescaped zod
template-literal sink; a single fix (escape `default` values) closes all of them, and a CNA may choose
to consolidate the related reports.

### PoC

`reproduce.sh` (+ `make_spec.py`) attached: generates the zod schema with default validation, bundles
it, imports it, and shows a marker written at import. Verified on 8.19.0.

### Impact

Code execution at import in any application that imports a zod schema module generated from an
attacker-controlled or attacker-influenced OpenAPI description.

### Suggested fix

Emit `default` values via a proper string-literal encoder (JSON.stringify, or escape backtick and `${`
if a template literal must be used); never interpolate a spec value into a template literal. Apply to
every `default` position.
[maintainer-report.txt](https://github.com/user-attachments/files/29399067/maintainer-report.txt)
[make_spec.py](https://github.com/user-attachments/files/29399068/make_spec.py)
[reproduce.sh](https://github.com/user-attachments/files/29399069/reproduce.sh)

## References
- https://github.com/orval-labs/orval/security/advisories/GHSA-p4cg-3328-rvfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-72716
- https://github.com/orval-labs/orval/pull/3692
- https://github.com/orval-labs/orval/commit/8ef1bfdf3f9bcaf9dabfbe2e42887f1c0e159ab6
- https://github.com/orval-labs/orval
- https://github.com/orval-labs/orval/releases/tag/v8.21.0
