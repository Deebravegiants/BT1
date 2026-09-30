# [H] brace-expansion: DoS via unbounded intermediate arrays, bypassing the CVE-2026-14257 mitigation

## Summary
Severity: High
Advisory: GHSA-rgw5-rvv9-x895
CVE: CVE-2026-69152
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-rgw5-rvv9-x895
Type: github-advisory

## Affected
- npm: `brace-expansion` — affected >=0 <1.1.18
- npm: `brace-expansion` — affected >=2.0.0 <2.1.4
- npm: `brace-expansion` — affected >=3.0.0 <3.0.6
- npm: `brace-expansion` — affected >=4.0.0 <5.0.9

## Details
### Summary

The `maxLength` mitigation added in `5.0.8` for GHSA-mh99-v99m-4gvg / CVE-2026-14257 is incomplete. It bounds the accumulator where results are *combined*, but not the intermediate arrays that feed it. A ~25 KB input still crashes the Node process with an **uncatchable** out-of-memory error, so `try/catch` around `expand()` does not help.

A second, related path in the same function lets a ~400 KB input block the event loop for over two minutes without ever exceeding the memory bound.

### Details

`maxLength` was enforced in `combine()`, the single place output grows. Two arrays are built *before* `combine()` runs, and neither was bounded.

**1. Comma alternatives accumulate without a running total (memory exhaustion)**

Each alternative in `{a,b,c,...}` is expanded by its own recursive `expand_()` call, so each receives a full, independent `maxLength` allowance. The results were then concatenated into a single `values` array with no cumulative limit:

```js
values = []
for (let j = 0; j < n.length; j++) {
  values.push.apply(values, expand_(n[j], max, maxLength, false))
}

acc = combine(acc, pre, values, max, maxLength, ...)
```

With `A` alternatives, `values` can reach `A * maxLength` characters before `combine()` gets a chance to truncate it. At the default `maxLength` of 4,000,000 and 400 alternatives, that is well past any default heap.

**2. Padded sequences ignore `maxLength` while generating (CPU exhaustion)**

`expandSequence()` was bounded by `max` (the result *count*) but never consulted `maxLength`. A padded sequence's element width follows the input, so `{0...01..100000}` with a wide pad generates `max` elements, each as wide as the input, only for `combine()` to discard all but a handful.

Memory stays flat here, because V8 represents the padded strings as cons-strings, which is likely why this path was not caught alongside the original issue. The cost is time: work proportional to `max * width`.

| pad width | input bytes | results kept | time (5.0.8) | time (patched) |
|---|---|---|---|---|
| 20,000 | 20 KB | 199 | ~7.3 s | ~20 ms |
| 100,000 | 100 KB | 39 | ~32 s | ~20 ms |
| 400,000 | 400 KB | 9 | ~124 s | ~18 ms |

Output is byte-identical before and after the fix; only the wasted work is removed.

### Proof of concept

Memory exhaustion, against `5.0.8`:

```js
import { expand } from 'brace-expansion'

const part = '{' + '0'.repeat(50) + '1..100000}'
const input = '{' + Array(400).fill(part).join(',') + '}'  // ~25 KB

try {
  expand(input)
} catch (e) {
  // never reached - the process is already dead
}
```

```
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
Aborted
```

Event-loop stall, against `5.0.8`:

```js
import { expand } from 'brace-expansion'

// ~400 KB input, returns 9 results after roughly two minutes of blocking CPU
expand('{' + '0'.repeat(400_000) + '1..100000}')
```

### Impact

Denial of service. Any application that passes attacker-controlled input to `expand()`, directly or transitively through a glob or pattern-matching library, can be remotely crashed or stalled. The out-of-memory variant terminates the process and cannot be handled with `try/catch`.

Applications already on `5.0.8` are affected: the `5.0.8` mitigation does not cover these paths.

### Patches

Both intermediate arrays are now bounded as they are built, using the same `max` and `maxLength` limits already applied in `combine()`:

- `values` tracks a running result count and character length while alternatives are appended, and stops once either bound is reached.
- `expandSequence()` accepts `maxLength` and stops generating once the sequence's own characters reach it.

As with the existing limits, output is truncated rather than allowed to grow without bound, which matches how `max` already behaves. The defaults sit well above any realistic expansion, so legitimate input is unaffected.

### Workarounds

If upgrading is not immediately possible, avoid passing untrusted input to `expand()` or to glob brace patterns, or pass an explicitly small `max` **and** `maxLength`.

Note that a small `maxLength` alone was not sufficient on affected versions: it was applied per alternative rather than cumulatively, which is the root of the first issue above.

### Credits

The memory-exhaustion bypass was reported by Alessio Della Libera, CEO & Co-founder at [Numyra](https://numyra.ai/).

The sequence-generation issue was found while verifying that report.

## References
- https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-rgw5-rvv9-x895
- https://nvd.nist.gov/vuln/detail/CVE-2026-69152
- https://github.com/juliangruber/brace-expansion/commit/139d015104e71433ad52a41d19467c48ecbb2c7d
- https://github.com/juliangruber/brace-expansion/commit/1e30c930238d7162802d88a94189182def178dac
- https://github.com/juliangruber/brace-expansion/commit/688a99eeaab02627c2b89ba8ba4821fecfa659cf
- https://github.com/juliangruber/brace-expansion/commit/cb4b9e47cc2ec777c14b2b4492fb431a56f6a031
- https://github.com/juliangruber/brace-expansion
