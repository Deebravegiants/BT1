# [H] DeepmergeTS has stack exhaustion when merging recursive object graphs

## Summary
Severity: High
Advisory: GHSA-ggr8-5vv4-36mx
CVE: CVE-2026-40345
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-ggr8-5vv4-36mx
Type: github-advisory

## Affected
- npm: `deepmerge-ts` — affected >=0 <8.0.0

## Details
### Summary

`deepmerge()` and `deepmergeInto()` can be crashed with a crafted recursive object graph. When both merged values contain self-references at the same property path, the library recurses until Node throws `RangeError: Maximum call stack size exceeded`.

### Details

Record merging is implemented recursively. For each enumerable key, the library collects the values from every input object and immediately calls the same merge routine on that property.

There is no visited-object tracking, pair tracking, or cycle detection in that recursion. As a result, if two merged records both point back to themselves through the same key path, the merge logic keeps revisiting the same object pair forever.

This is reachable through the real public API:

* `deepmerge(...)`
* `deepmergeCustom(...)(...)`
* `deepmergeInto(target, ...)`
* `deepmergeIntoCustom(...)(target, ...)`

The issue only occurs when recursive object graphs are supplied. Plain JSON alone does not create this condition.

### PoC

```js
import { deepmerge, deepmergeInto } from "deepmerge-ts";

const left = {};
left.self = left;

const right = {};
right.self = right;

try {
  deepmerge(left, right);
} catch (error) {
  console.log(error.name, error.message);
  // Expected: the merge should reject or safely handle recursive input without exhausting the stack.
  // Vulnerable behavior: RangeError Maximum call stack size exceeded
}

const target = {};
target.self = target;

const source = {};
source.self = source;

try {
  deepmergeInto(target, source);
} catch (error) {
  console.log(error.name, error.message);
  // Expected: the merge should reject or safely handle recursive input without exhausting the stack.
  // Vulnerable behavior: RangeError Maximum call stack size exceeded
}
```

### Impact

Applications that pass attacker-controlled recursive object graphs into these APIs can be forced into a synchronous crash path. In Node.js services, that can terminate request handling for the affected process or trigger repeated worker restarts until the malicious input is blocked.

## References
- https://github.com/RebeccaStevens/deepmerge-ts/security/advisories/GHSA-ggr8-5vv4-36mx
- https://github.com/RebeccaStevens/deepmerge-ts
- https://github.com/RebeccaStevens/deepmerge-ts/releases/tag/v8.0.0
