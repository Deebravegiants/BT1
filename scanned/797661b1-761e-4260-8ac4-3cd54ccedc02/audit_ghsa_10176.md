# [H] @stablelib/cbor: Stack exhaustion Denial of Service via deeply nested CBOR arrays, maps, or tags

## Summary
Severity: High
Advisory: GHSA-5jg4-p4qw-cgfr
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-5jg4-p4qw-cgfr
Type: github-advisory

## Affected
- npm: `@stablelib/cbor` — affected >=0 <2.0.3

## Details
### Summary

`@stablelib/cbor` decodes nested CBOR structures recursively and does not enforce a maximum nesting depth. A sufficiently deep attacker-controlled CBOR payload can therefore crash decoding with `RangeError: Maximum call stack size exceeded`.

### Details

The decoder processes arrays, maps, and tagged values through recursive calls. Each nested container causes another descent into `_decodeValue()` until a leaf value is reached.

There is no depth limit, no iterative fallback, and no protection against pathological nesting. An attacker can therefore supply a payload made of thousands of nested arrays, maps, or tags and force the decoder to recurse until the JavaScript call stack is exhausted.

### PoC

```js
import { decode } from "@stablelib/cbor";

const depth = 12000;
const payload = new Uint8Array(depth + 1);

// Build [[[...[null]...]]]
payload.fill(0x81, 0, depth); // array(1)
payload[depth] = 0xf6;        // null

decode(payload);
// RangeError: Maximum call stack size exceeded
```

### Impact

Any application that decodes attacker-controlled CBOR can be forced into a reliable denial of service with a single crafted payload.

The immediate result is an exception during decoding. In services that do not catch that exception safely, the request fails and the worker or process handling the decode may terminate.


### Solution

Upgrade to version 2.0.4. The stack is limited to 128 by default, but can be configured using the `maxDepth` option. Catch the `CBORMaxDepthExceededError` exception.

## References
- https://github.com/StableLib/stablelib/security/advisories/GHSA-5jg4-p4qw-cgfr
- https://github.com/StableLib/stablelib/commit/0149e18d9d4736e22c257744ca945ebce7899a01
- https://github.com/StableLib/stablelib
