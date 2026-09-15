# [M] op_panic in the base runtime can force a panic in the runtime's containing thread

## Summary
Severity: Medium
Advisory: GHSA-4mw5-2636-4535
Ecosystem: crates.io
Published: 2024-12-04
Source: https://github.com/advisories/GHSA-4mw5-2636-4535
Type: github-advisory

## Affected
- crates.io: `js-sandbox` — affected >=0

## Details
Affected versions use deno_core releases that expose `Deno.core.ops.op_panic` to the JS runtime in the base core

This function when called triggers a manual panic in the thread containing the runtime, breaking sandboxing

It can be fixed by stubbing out the exposed op:
```javascript
Deno.core.ops.op_panic = (msg) => { throw new Error(msg) };
```

## References
- https://github.com/Bromeon/js-sandbox/issues/31
- https://github.com/Bromeon/js-sandbox
- https://rustsec.org/advisories/RUSTSEC-2024-0403.html
