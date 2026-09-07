# [H] Immutable.js `List` 32-bit trie overflow → unrecoverable DoS

## Summary
Severity: High
Advisory: GHSA-v56q-mh7h-f735
CVE: CVE-2026-59879
CWE: CWE-1284, CWE-190, CWE-400, CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-v56q-mh7h-f735
Type: github-advisory

## Affected
- npm: `immutable` — affected >=0 <4.3.9
- npm: `immutable` — affected >=5.0.0-beta.1 <5.1.8

## Details
## Summary

`List#set`, `List#setSize`, `List#setIn`, `List#updateIn` (and the functional `set` / `setIn` / `updateIn`) mishandle an index or size in the range `[2 ** 30, 2 ** 31)`:

- On an **empty** `List` the operation enters an **uncatchable infinite loop** (a tight CPU spin; a surrounding `try/catch` never regains control). Only killing the worker recovers it.
- On a **populated** `List` (≥ 32 elements — i.e. any array of ≥ 32 items turned into a `List` by `fromJS`) the loop allocates without bound → heap exhaustion → the **process aborts** (`SIGABRT`, exit `134`, or kernel OOM-kill `137`). A real crash, not a recoverable error.

The index may be a **numeric string**, so it can come straight from a request body, URL, or key-path. A single small unauthenticated request is enough.

There is also a companion **silent data-corruption** issue in `setSize`:

```js
List([1, 2, 3]).setSize(2 ** 31); // before fix => size 0  (silently cleared)
List([1, 2, 3]).setSize(2 ** 32 + 5); // before fix => size 5  (huge value wraps to 5)
```

## Impact

Availability only. A reachable configuration is any endpoint that routes untrusted input into a `List` index or a `setIn`/`updateIn` key-path — which the extremely common `state = fromJS(body); state.setIn(userPath, value)` pattern does (config stores, document/collection editors, redux-immutable reducers, JSON-Patch endpoints, etc.).

No confidentiality or integrity impact, no RCE. The companion `setSize` bug can silently corrupt application state (wrong size) without crashing.

## Reproduction (immutable 5.1.7)

```ts
import { fromJS, List } from 'immutable';

// 1) Populated List: OOM -> process abort (SIGABRT, exit 134) within ~2s
fromJS({ items: new Array(64).fill(0) }).setIn(['items', '1073741824'], 'x');

// 2) Empty List: hangs forever, uncatchable
List().set(2 ** 30, 'x');

// 3) Silent truncation
List([1, 2, 3]).setSize(2 ** 31); // => size 0
List([1, 2, 3]).setSize(2 ** 32 + 5); // => size 5
```

A remote 43-byte HTTP request (`{"path":["items","1073741824"],"value":"x"}`) is sufficient to abort a worker that applies it via `state = state.setIn(path, value)`.

Any index in `[2 ** 30, 2 ** 31)` works (`1073741824`, `2000000000`, …). An index in `[2 ** 31, 2 ** 32)` does not crash — it silently wraps (clearing the List) via the same root cause.

## Root cause

`List` stores its values in a 32-wide trie (`SHIFT = 5`, so each level addresses 5 more bits) and uses **signed 32-bit bitwise arithmetic** throughout `setListBounds()` (`src/List.js`):

1. **Infinite loop (the hang / OOM).** The level-raising loop

```js
while (newTailOffset >= 1 << (newLevel + SHIFT)) {
  newRoot = new VNode(
    newRoot && newRoot.array.length ? [newRoot] : [],
    owner
  );
  newLevel += SHIFT;
}
```

relies on `1 << (newLevel + SHIFT)`. A JavaScript shift count is taken **mod 32**, so once `newLevel + SHIFT` reaches `31` the term goes **negative** (`1 << 31 === -2147483648`) and at `32` wraps to `1` (`1 << 35 === 8`). The comparison then stays `true` forever and the loop never terminates. On a populated `List`, each iteration retains a new `VNode` (`[newRoot]`), so the heap fills and V8 aborts; on an empty `List` it spins on CPU without allocating.

2. **Silent wraparound (the `setSize` corruption).** The `begin |= 0` / `end |= 0` coercion (`ToInt32`) silently wraps large finite values (`(2 ** 31) | 0 === -2147483648`, `(2 ** 32 + 5) | 0 === 5`), producing a wrong resulting size instead of an error.

The threshold is `2 ** 30`: that is the largest size for which `1 << (newLevel + SHIFT)` stays a valid positive 32-bit integer throughout the loops (`newLevel + SHIFT` stays ≤ 30).

## Remediation

The fix is contained to `setListBounds()` in `src/List.js`:

1. **Validate up front, before the lossy `| 0` coercion.** Compute the intended origin and capacity in full precision and throw a clear, catchable `RangeError` when they exceed the addressable range (`MAX_LIST_SIZE = 2 ** 30`). `Infinity`/`NaN` are left to the existing `| 0 → 0` behaviour (so `setSize(Infinity)` stays `0` and `slice(0, Infinity)` still means "to the end").

2. **Stop the shift from wrapping.** Replace `1 << exp` in the level-raising loops with a helper that uses the cheap bitwise shift while it is exact (`exp ≤ 30`, the common path including every `push`/`setSize`/`slice`) and falls back to the non-wrapping `2 ** exp` only for the rare deep trees reached when a negative origin (`unshift` / negative index) is normalized to a large positive capacity (`exp` can reach 35 there, where `1 << 35` would wrap to 8).

This turns every hang, the misleading `"Maximum call stack size exceeded"`, the OOM/`SIGABRT`, and the silent `setSize` truncation into one descriptive `RangeError`, preserves all behaviour for sizes `< 2 ** 30`, and keeps the hot `push` path on the fast bitwise shift (the `2 ** exp` branch is never reached by non-negative operations).

### Is the new limit a breaking change?

No working code is affected. A `List` could never actually hold `≥ 2 ** 30` values before — the attempt hung, crashed, or silently corrupted the size. The limit was already implicit in the 32-bit trie; the fix only makes it explicit and catchable, mirroring native JS arrays (`new Array(2 ** 32)` → `RangeError: Invalid array length`). The single observable behaviour change is that `setSize(hugeValue)`, which used to return a silently wrong size, now throws. `2 ** 30` ≈ 1.07 billion entries (~8 GB of pointers alone), far beyond any practical use.

## Mitigations (for users who cannot upgrade immediately)

- Validate/clamp any externally supplied `List` index or `setIn`/`updateIn` key-path segment against a sane maximum before passing it to immutable.
- Reject numeric path segments `≥ 2 ** 30`.
- Run request handling in a worker that can be restarted, and cap the heap (`--max-old-space-size`) so an abort is contained.

## References
- https://github.com/immutable-js/immutable-js/security/advisories/GHSA-v56q-mh7h-f735
- https://nvd.nist.gov/vuln/detail/CVE-2026-59879
- https://github.com/immutable-js/immutable-js/commit/a1a1ee412dcaa380ab325196283d06594ffe4b84
- https://github.com/immutable-js/immutable-js/commit/f0bc997d8eb9886aff2236635aa210a95a04304a
- https://github.com/immutable-js/immutable-js
- https://github.com/immutable-js/immutable-js/releases/tag/v4.3.9
- https://github.com/immutable-js/immutable-js/releases/tag/v5.1.8
