# [H] Browserslist: Unbounded memory growth (no cache eviction) via distinct query results, leading to eventual OOM

## Summary
Severity: High
Advisory: GHSA-c83g-rgw3-j3cx
CVE: CVE-2026-73089
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-c83g-rgw3-j3cx
Type: github-advisory

## Affected
- npm: `browserslist` — affected >=0 <4.28.7

## Details
## Vulnerability Details

**File**: `index.js`
**Location**: `cache` (browserslist()'s result cache, line ~402) and
`parseCache` (parseQueries()'s AST cache)

### Root Cause
```js
var cache = {}
var parseCache = {}

function browserslist(queries, opts) {
  ...
  var cacheKey = JSON.stringify([queries, context])
  if (cache[cacheKey]) return cache[cacheKey]
  ...
  if (!env.env.BROWSERSLIST_DISABLE_CACHE) { cache[cacheKey] = result }
  return result
}

function parseQueries(queries) {
  var cacheKey = JSON.stringify(queries)
  if (cacheKey in parseCache) return parseCache[cacheKey]
  var result = parseWithoutCache(QUERIES, queries)
  if (!env.env.BROWSERSLIST_DISABLE_CACHE) { parseCache[cacheKey] = result }
  ...
}
```
Every distinct `(queries, context)` pair is cached forever — no size cap,
TTL, or eviction. `browserslist.clearCaches()` never resets either object
(it only resets `node.js`'s own filesystem caches); the only opt-out is the
`BROWSERSLIST_DISABLE_CACHE` env var, controlled by the *calling
application*, not an attacker.

Some short, valid queries amplify this badly. The `since <year>-<month>-<day>`
query type (`/^since (\d+)-(\d+)-(\d+)$/i`) accepts **any** digit
combination — `Date.UTC()` normalizes rather than rejects out-of-range
values — giving an effectively unbounded space of ~17-byte distinct cache
keys, each of which resolves to (and caches) a result close to the full
~8.5 KB browser list for any sufficiently old year.

### Measured Impact
20,000 distinct `since <year>-<month>-<day>` queries (~330 KB total input,
`--expose-gc` before/after measurement to rule out uncollected garbage)
retained **over 50 MB** of heap permanently — roughly **150x**
amplification, growing linearly with no cap observed up to 40,000 queries
(52.3 MB).

### Attack Scenario
Any long-running process (server, daemon, warm CI worker) that calls
`browserslist()` with a query value that varies across requests/items and is
influenced, even partially, by external input accumulates one cache entry
per distinct value ever seen. An attacker who can influence that value
across *many* requests (this is a volumetric attack, unlike the
single-request DoS findings from this same research pass) sends a stream of
cheap, distinct queries (e.g. `since 1900-01-01`, `since 1900-01-02`, ...)
until the process runs out of memory and crashes.

### Recommended Fix (implemented and verified)
Replace both plain-object caches with `Map`s bounded to a fixed maximum
entry count, evicting the oldest entry once the cap is reached (`Map`
preserves insertion order, so `.keys().next().value` is always oldest):

```js
var CACHE_MAX_ENTRIES = 500

function boundedCacheSet(map, key, value) {
  if (map.size >= CACHE_MAX_ENTRIES) {
    map.delete(map.keys().next().value)
  }
  map.set(key, value)
}

var cache = new Map()
var parseCache = new Map()
```
(read sites changed to `.has()`/`.get()`, write sites to `boundedCacheSet()`)

**Verification**:
- `NODE_ENV=test npx uvu test .test.js` → 301/301 pass unmodified
  (`test/cache.test.js` exercises `clearCaches()`/`BROWSERSLIST_DISABLE_CACHE`
  against `node.js`'s separate filesystem caches, unaffected here); confirmed
  a repeated identical call still returns the cached reference.
- Re-ran the memory PoC post-fix: heap stayed flat at ~4.9 MB after 5,000,
  10,000, 20,000, and 40,000 distinct `since`-date queries (was
  10.5 → 16.5 → 28.4 → 52.3 MB pre-fix).

### Impact
- **Who is affected**: Long-running processes calling `browserslist()` with
  query values that vary across requests/items and are influenced by
  external input.
- **What an attacker achieves**: DoS via eventual out-of-memory crash, given
  sustained traffic over time (not a single small payload).
- **Conditions required**: No authentication; requires volume rather than a
  single request, hence Medium rather than High severity.

### Verification Environment
browserslist @ HEAD (== v4.28.6, current latest stable release) under local
Node.js v20.19.5, run with `--expose-gc` for accurate heap measurement.

### Note
Found during a broader review of this codebase in the same research pass
that produced GHSA-rrmg-cfrq-23vv (parse.js algorithmic complexity),
GHSA-g6p8-hj8g-x889 (baseline regexp ReDoS), GHSA-73wf-gq98-2v4g
(normalizeStats crash/prototype write), and GHSA-h633-868p-5rfw
(SCOPED_CONFIG__PATTERN ReDoS) — all single-request DoS vectors. This one is
different in character (volumetric, not single-request) and is reported
separately/scored lower accordingly.

## References
- https://github.com/browserslist/browserslist/security/advisories/GHSA-c83g-rgw3-j3cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-73089
- https://github.com/browserslist/browserslist/commit/f2931a3ff2a3a31abf84ef01a7400b270aad6405
- https://github.com/browserslist/browserslist
- https://github.com/browserslist/browserslist/releases/tag/4.28.7
