# [H] LiquidJS: `pop` filter bypasses `memoryLimit` accounting that its array-filter siblings enforce

## Summary
Severity: High
Advisory: GHSA-g357-x5c3-c72p
CVE: CVE-2026-55575
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/ (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-g357-x5c3-c72p
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.27.1

## Details
# `pop` filter bypasses `memoryLimit` accounting that its array-filter siblings enforce

**CWE**: CWE-770 (Allocation of Resources Without Limits or Throttling) — sibling class of GHSA-8xx9-69p8-7jp3 and GHSA-2546-xv4c-mc8g, applied to `memoryLimit` instead of `renderLimit`

## Summary

The `pop` array filter at `src/filters/array.ts:91-95` allocates a full clone of its input array via `[...toArray(v)]` but does **not** call `this.context.memoryLimit.use(...)` the way every other array-clone filter in the same file does (`shift`, `unshift`, `compact`, `concat`, `reverse`, `sample`, `slice`, `map`, `sortBy`, `where`, `group_by`, `uniq`). This silently disables the `memoryLimit` budget for `{{ huge_array | pop }}`, letting a template render allocate an O(N) clone of an attacker-influenced array regardless of how strictly `memoryLimit` is set.

## Affected

- liquidjs ≥ all versions that ship the current `pop` filter implementation (verified `10.27.0`, HEAD `a8fd734b5`)
- Deployments where any template uses `{{ arr | pop }}` on an array whose length is influenced by untrusted input (typical multi-tenant context arrays: orders, log lines, catalog entries, user lists, etc.)

## Vulnerability details

### Code

`src/filters/array.ts:91-95`:

```ts
export function pop<T> (v: T[]): T[] {
  const clone = [...toArray(v)]   // O(N) allocation — not charged to memoryLimit
  clone.pop()
  return clone
}
```

Note: the function signature does not even declare `this: FilterImpl`, so it has no typed access to `this.context.memoryLimit` at the type level — a visual tell that the author skipped the limit-accounting boilerplate the surrounding filters use.

Compare with `shift` (`src/filters/array.ts:97-103`), which is functionally identical except for the array-end operated on:

```ts
export function shift<T> (this: FilterImpl, v: T[]): T[] {
  const array = toArray(v)
  this.context.memoryLimit.use(array.length)   // ← guard present
  const clone = [...array]
  clone.shift()
  return clone
}
```

And `unshift`, `compact`, `concat`, `reverse`, `sample`, `slice`, `map`, `sortBy`, `where`, `group_by`, `uniq` — all of which also charge `memoryLimit.use(array.length)` (or `lhs.length + rhs.length` etc.) before allocating their working buffer.

The asymmetry confirms `pop` is an accidental omission, not by design.

### Why the bypass matters

`memoryLimit` is the documented control for bounding the memory a single `render()` call may allocate (`docs/source/tutorials/dos.md`). Every array-output filter in `src/filters/array.ts` other than `pop` deducts its working set from the limit, so a render that does `{{ huge | shift }}` with `memoryLimit: 100` and `huge.length === 5_000_000` correctly throws `memory alloc limit exceeded`. The identical `{{ huge | pop }}` does **not** throw — the allocation proceeds, and the only ceiling is the Node process's heap.

## Proof of concept

```js
const { Liquid } = require('liquidjs');

const l    = new Liquid({ memoryLimit: 100 });        // 100-unit budget
const huge = Array(5_000_000).fill('x');              // 5M-element context array

(async () => {
  try { await l.parseAndRender('{{ a | shift | size }}', { a: huge }); }
  catch (e) { console.log('shift:   ' + e.message); }      // expected: memory alloc limit exceeded

  try { await l.parseAndRender('{{ a | unshift: 0 | size }}', { a: huge }); }
  catch (e) { console.log('unshift: ' + e.message); }      // expected: memory alloc limit exceeded

  const out = await l.parseAndRender('{{ a | pop | size }}', { a: huge });
  console.log('pop:     OK, size=' + out);                  // size=4999999 — allocation succeeded
})();
```

Observed (against `dist/liquid.node.js` at `a8fd734b5`):

```
shift:   memory alloc limit exceeded, line:1, col:1
unshift: memory alloc limit exceeded, line:1, col:1
pop:     OK, size=4999999
```

## Impact

- **`memoryLimit` does not bound `pop` allocations.** Any template that can reach `{{ <untrusted-sized array> | pop }}` allocates an O(N) clone outside the budget.
- **Realistic attack surface**: when a server passes an attacker-influenced large array to the template context (search results, paginated lists, batch-export pages) and the template uses `| pop` anywhere on it, a single render can allocate hundreds of MB of array slots that the operator believed `memoryLimit` had ruled out.
- **Concurrent amplification**: N parallel requests each allocate their own unguarded clone — the practical ceiling is the Node process heap, after which the host runs `oom-kill`. This is the same outcome the renderLimit-empty-body advisories (GHSA-8xx9-69p8-7jp3 / GHSA-2546-xv4c-mc8g) prevented for CPU; this report prevents it for memory.

Severity is configuration-dependent (requires `memoryLimit` to be set, plus a template that uses `pop`, plus attacker-influenced array length). For deployments that rely on `memoryLimit` as a DoS guard, this is a real bypass of that guard.

## Workaround for users

Until a fix lands, deployments relying on `memoryLimit` should either:

- Avoid `| pop` in templates whose inputs include untrusted-length arrays. Use `| slice: 0, arr.size | minus: 1` or equivalent guarded alternatives.
- Register a wrapping `pop` filter that does the accounting:

  ```js
  liquid.registerFilter('pop', function (v) {
    const arr = Array.from(v ?? []);
    this.context.memoryLimit.use(arr.length);
    arr.pop();
    return arr;
  });
  ```

## Suggested fix

One-line addition mirroring `shift`:

```ts
export function pop<T> (this: FilterImpl, v: T[]): T[] {
  const array = toArray(v)
  this.context.memoryLimit.use(array.length)   // ← add this line, and add `this: FilterImpl`
  const clone = [...array]
  clone.pop()
  return clone
}
```

No API or behavior change for callers within budget; rejects out-of-budget calls with the standard `memory alloc limit exceeded` exception the sibling filters already throw.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-g357-x5c3-c72p
- https://nvd.nist.gov/vuln/detail/CVE-2026-55575
- https://github.com/harttle/liquidjs/pull/907
- https://github.com/harttle/liquidjs/commit/8a0c74a7fcb1671aa1dcb71ec82ba0602dc90d04
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.27.1
