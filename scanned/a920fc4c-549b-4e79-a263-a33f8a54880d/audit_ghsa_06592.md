# [H] shell-quote: Quadratic-complexity Denial of Service in `parse()` (CWE-407)

## Summary
Severity: High
Advisory: GHSA-395f-4hp3-45gv
CVE: CVE-2026-13311
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-395f-4hp3-45gv
Type: github-advisory

## Affected
- npm: `shell-quote` — affected >=0 <1.9.0

## Details
### Summary
`shell-quote`'s `parse()` finalizes its token list with a `reduce` that uses
`Array.prototype.concat` as the accumulator. Each `prev.concat(arg)` copies the entire growing
array, so `parse()` runs in **O(n²)** in the number of tokens. An unauthenticated attacker who
can submit a string to any code path that calls `parse()` on it can block the single-threaded
Node.js event loop for tens of seconds with a small input — a denial of service. The trigger
needs **no shell metacharacters** (plain space-separated words suffice), so input filters that
only screen for `;`, `|`, `$`, or backticks do not help.

### Root cause
`parse.js` (lines 200–203), in `parseInternal` — this path runs on **every** `parse()` call:

```js
}).reduce(function (prev, arg) { // finalize parsed arguments
    // TODO: replace this whole reduce with a concat
    return typeof arg === 'undefined' ? prev : prev.concat(arg);
}, []);
```

`prev.concat(arg)` allocates a new array and copies all of `prev` on every iteration, so
producing an N-token result costs `1 + 2 + … + N = O(N²)` copies. A second `acc.concat(s)`
reduce in the `module.exports` wrapper (lines 211–224, reached only when `env` is a function)
has the same shape. The maintainer's own `// TODO: replace this whole reduce with a concat`
already flags the construct.

### Proof of Concept
```js
const { parse } = require('shell-quote');
const ms = fn => { const t = process.hrtime.bigint(); fn(); return Number(process.hrtime.bigint()-t)/1e6; };
for (const N of [16000, 32000, 64000, 128000]) {
  console.log(N, 'tokens ->', ms(() => parse('x '.repeat(N))).toFixed(0), 'ms');
}
```

Measured on `shell-quote@1.8.4`, Node v24:

| input (N tokens) | bytes  | `parse()` | ratio vs prev (2× input) |
|-----------------:|-------:|----------:|:------------------------:|
| 16 000           | 32 KB  |    678 ms | —                        |
| 32 000           | 64 KB  |  4 169 ms | ×6.2                     |
| 64 000           | 128 KB | 14 914 ms | ×3.6                     |
| 128 000          | 256 KB | **57 319 ms** | ×3.8                 |

Time grows ~×4 per 2× input → confirmed O(n²). A ~128 KB input blocks the event loop ~15 s;
~256 KB → ~57 s; a few hundred KB more → minutes.
<img width="656" height="214" alt="image" src="https://github.com/user-attachments/assets/e8955b0e-0527-45ca-94b7-c3a2d8c0c82e" />
[poc.js](https://github.com/user-attachments/files/29255995/poc.js)

### Impact
`parse()` is synchronous on the main thread; while it copies arrays quadratically the entire
event loop is blocked and the process serves no other requests. Any service that calls `parse()`
on attacker-influenced input (command parsers, chat-ops / bot command handlers, REPLs,
build-script / arg-string splitters) can be driven to a sustained DoS with a single small
request. No code execution and no data disclosure — availability only.

End-to-end confirmation: a minimal HTTP server that calls `parse()` on the request body, hit
with **one** `POST` of `'x '.repeat(32000)` (~63 KB), froze for ~4.5 s. An out-of-process probe
client issuing harmless `GET /ping` requests (normally ~1 ms) observed **27 consecutive pings
stalled by up to 4374 ms** during that single request — i.e. every concurrent client was denied
service for the whole parse. Scaling the body to a few hundred KB extends the outage to minutes.

This is the same class as several accepted 2026 advisories for quadratic-parser DoS on
untrusted input (e.g. markdown-it CVE-2026-48988, js-yaml CVE-2026-53550,
python-multipart CVE-2026-53539). It is **distinct** from the known `shell-quote`
command-injection issues (CVE-2021-42740, CVE-2016-10541, CVE-2026-9277), which are all in
`quote()`, not `parse()`.

### Suggested remediation
Replace the O(n²) concat-in-reduce with a linear flatten that **pushes into the
accumulator** instead of reallocating and copying it on every iteration. Apply the
same shape to the wrapper's `acc.concat(s)` reduce. A defensive input-length cap on
`parse()` is a cheap additional stop-gap.

> **Maintainer note (edit):** the originally-suggested `Array.prototype.flat()` is
> ES2019 / Node 11+, but `shell-quote` declares `engines: node >= 0.4`, so `.flat()`
> would silently drop support for older runtimes. The fix instead flattens one-level
> array tokens with `forEach`/`push` — and deliberately not `push.apply(...)`, since
> spreading a large array into function arguments can exceed the engine's argument
> count limit. Output is byte-identical to the current code across strings, `undefined`
> holes, one-level array tokens, and `{op}`/`{comment}`/`{op:'glob'}` objects, and
> finalizing is now linear (1,024,000 tokens in ~150 ms vs ~57 s for 128,000 before).
> Thanks for the clear report and PoC — the analysis and reproduction were spot on.

### Disclosure
Found by source audit + wall-clock confirmation against 1.8.4 (and verified the same code is
present on `main`). Reported privately here; no public disclosure until a fix is available.

## References
- https://github.com/ljharb/shell-quote/security/advisories/GHSA-395f-4hp3-45gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-13311
- https://github.com/ljharb/shell-quote/commit/7ff5488599d01c323514f02f5efb74088dd134ec
- https://github.com/ljharb/shell-quote
- https://github.com/ljharb/shell-quote/releases/tag/v1.9.0
- https://www.npmjs.com/package/shell-quote
