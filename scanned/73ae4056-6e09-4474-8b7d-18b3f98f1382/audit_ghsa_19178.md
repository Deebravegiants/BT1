# [M] Vega allows Cross-site Scripting via the vlSelectionTuples function

## Summary
Severity: Medium
Advisory: GHSA-mp7w-mhcv-673j
CVE: CVE-2025-25304
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-mp7w-mhcv-673j
Type: github-advisory

## Affected
- npm: `vega` — affected >=0 <5.26.0
- npm: `vega-selections` — affected >=0 <5.4.2

## Details
### Summary
The `vlSelectionTuples` function can be used to call JavaScript functions, leading to XSS.

### Details
[`vlSelectionTuples`](https://github.com/vega/vega/blob/b45cf431cd6c0d0c0e1567f087f9b3b55bc236fa/packages/vega-selections/src/selectionTuples.js#L14) calls multiple functions that can be controlled by an attacker, including one call with an attacker-controlled argument.

Example call: `vlSelectionTuples([{datum:<argument>}], {fields:[{getter:<function>}]})`

This can be used to call `Function()` with arbitrary JavaScript and the resulting function can be called with `vlSelectionTuples` or using a type coercion to call `toString` or `valueOf`.

### PoC
```
{"$schema":"https://vega.github.io/schema/vega/v5.json","signals":[{"name":"a","init":"+{valueOf:vlSelectionTuples([{datum:'alert(1)'}],{fields:[{getter:[].at.constructor}]})[0].values[0]}"}]}
```

## References
- https://github.com/vega/vega/security/advisories/GHSA-mp7w-mhcv-673j
- https://nvd.nist.gov/vuln/detail/CVE-2025-25304
- https://github.com/vega/vega/commit/9fb9ea07e27984394e463d286eb73944fa61411e
- https://github.com/vega/vega
- https://github.com/vega/vega/blob/b45cf431cd6c0d0c0e1567f087f9b3b55bc236fa/packages/vega-selections/src/selectionTuples.js#L14
