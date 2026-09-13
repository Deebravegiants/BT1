# [H] Browserslist: Uncaught crash / prototype write via untrusted browserslist-stats.json custom stats (normalizeStats)

## Summary
Severity: High
Advisory: GHSA-73wf-gq98-2v4g
CVE: CVE-2026-73088
CWE: CWE-1321, CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-73wf-gq98-2v4g
Type: github-advisory

## Affected
- npm: `browserslist` — affected >=0 <4.28.7

## Details
## Vulnerability Details

**File**: `node.js`
**Function**: `normalizeStats()` (line ~214), reached from `getStat()` (called
**unconditionally** on every `browserslist()` call) and `loadStat()`

### Root Cause
```js
function normalizeStats(data, stats) {
  if (!data) { data = {} }
  if (stats && 'dataByBrowser' in stats) { stats = stats.dataByBrowser }
  if (typeof stats !== 'object') return undefined

  var normalized = {}
  for (var i in stats) {
    var versions = Object.keys(stats[i])
    if (versions.length === 1 && data[i] && data[i].versions.length === 1) {
      var normal = data[i].versions[0]
      normalized[i] = {}
      normalized[i][normal] = stats[i][versions[0]]
    } else {
      normalized[i] = stats[i]
    }
  }
  return normalized
}
```
`stats` is untrusted: it comes from `JSON.parse()`-ing a
`browserslist-stats.json` file — auto-discovered by walking up the directory
tree from the project root **on every `browserslist()` call, regardless of
the query** (`env.getStat(opts, browserslist.data)` runs unconditionally
inside `browserslist()`) — or from `opts.stats` passed programmatically /
via the CLI's `--stats=` flag. `data` is `browserslist.data`, a plain object
populated only with real browser names.

Two independent bugs from the same root cause (unguarded `for...in` over
untrusted keys used with plain-object bracket access/assignment):

1. **Crash**: `data[i]` has no `hasOwnProperty` guard. If `stats` contains a
   key that also happens to be an inherited `Object.prototype` member name —
   `"__proto__"`, `"toString"`, `"valueOf"`, `"constructor"`,
   `"hasOwnProperty"`, `"isPrototypeOf"`, etc. — `data[i]` resolves to that
   inherited function/object (always truthy), and the code then does
   `data[i].versions.length` → `undefined.length` → **uncaught `TypeError`**,
   for any such key whose JSON value has exactly one sub-key, e.g.:
   ```json
   { "toString": { "onekey": 5 }, "chrome": { "100": 50 } }
   ```
2. **Prototype write**: `normalized[i] = ...` on the fresh
   `normalized = {}` — if `i` is exactly `"__proto__"` (and `normalized` has
   no own property by that name yet), this computed assignment invokes the
   real `Object.prototype.__proto__` setter, changing `normalized`'s actual
   `[[Prototype]]` instead of creating a plain property.

Because this runs on **every** `browserslist()` call regardless of the
query, simply committing a poisoned `browserslist-stats.json` anywhere in a
project's directory tree breaks every subsequent Browserslist call in that
project — including calls made by Autoprefixer, Babel `preset-env`,
Stylelint, or PostCSS internally, for completely unrelated queries.

### Attack Scenario
1. Attacker submits a PR (or a compromised dependency) adding a
   `browserslist-stats.json` file anywhere between the project root and
   filesystem root, containing e.g.
   `{"toString": {"onekey": 5}, "chrome": {"100": 50}}`.
2. The victim's build/CI pipeline runs any tool that calls `browserslist()`
   internally, for **any** query.
3. The auto-discovered poisoned file crashes the process with an uncaught
   `TypeError` on the very first call.

### Measured Impact
Confirmed crash (real `browserslist()` call, v4.28.6) with `stats` keys:
`__proto__`, `toString`, `valueOf`, `hasOwnProperty`, `constructor`,
`isPrototypeOf` — each paired with a one-key JSON object — for any query,
including `browserslist('defaults')` which never mentions stats.

### Recommended Fix (implemented and verified)
```js
var normalized = Object.create(null)
for (var i in stats) {
  var versions = Object.keys(stats[i])
  var known = Object.prototype.hasOwnProperty.call(data, i) && data[i]
  if (versions.length === 1 && known && known.versions.length === 1) {
    var normal = known.versions[0]
    normalized[i] = Object.create(null)
    normalized[i][normal] = stats[i][versions[0]]
  } else {
    normalized[i] = stats[i]
  }
}
return normalized
```
`normalized` uses `Object.create(null)` so a write to `"__proto__"` is an
ordinary property set, never a `[[Prototype]]` change; `data[i]` is replaced
with an explicit `hasOwnProperty` check so it never resolves to an inherited
`Object.prototype` member.

**Verification**:
- `NODE_ENV=test npx uvu test .test.js` → 301/301 pass unmodified
  (`test/custom.test.js`, `test/shareable-stats.test.js`, `test/cover.test.js`
  exercise the stats-handling paths).
- All 6 previously crash-inducing keys, tested individually, now resolve
  without error.
- The realistic file-based auto-discovery scenario (poisoned
  `browserslist-stats.json` + an unrelated `browserslist('defaults')` call)
  now returns a normal result instead of crashing.

### Impact
- **Who is affected**: Any project whose build/CI invokes Browserslist
  (directly or via Autoprefixer/Babel/Stylelint/PostCSS) in a directory tree
  an attacker can place a file into (external PR, compromised dependency),
  or any app that passes user-influenced data into `opts.stats`.
- **What an attacker achieves**: Immediate DoS — crashes the invoking
  process on the first Browserslist call after the file is present, for any
  query, no special syntax needed.
- **Conditions required**: No authentication — only the ability to add a
  file to the project's directory tree, or influence `opts.stats`.

### Verification Environment
browserslist @ HEAD (== v4.28.6, current latest stable release) under local
Node.js v20.19.5. Pure JS library — executed directly, no server needed.

### Note
Found via a systematic review of prototype-pollution-adjacent patterns in
this codebase after confirming two unrelated algorithmic-complexity issues
(reported separately as GHSA-rrmg-cfrq-23vv and GHSA-g6p8-hj8g-x889) in the
same research pass. A similar `for...in` + bracket-write pattern in
`index.js`'s `copyObject()` (used by `normalizeAndroidData`) was already
guarded against `__proto__`/`constructor`/`prototype` keys by a prior,
unrelated commit — that guard was never applied to this function.

## References
- https://github.com/browserslist/browserslist/security/advisories/GHSA-73wf-gq98-2v4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-73088
- https://github.com/browserslist/browserslist/commit/f9914ad9effc865ccc27d816255625890b31ca51
- https://github.com/browserslist/browserslist
- https://github.com/browserslist/browserslist/releases/tag/4.28.7
