# [M] re2: Global `String.prototype.match` with an empty-matchable pattern never advances → infinite loop with unbounded native memory growth (DoS)

## Summary
Severity: Medium
Advisory: GHSA-6hxr-mr5r-9836
CVE: CVE-2026-68499
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-6hxr-mr5r-9836
Type: github-advisory

## Affected
- npm: `re2` — affected >=0 <1.25.2

## Details
## Summary

`String.prototype.match` with a **global** `RE2` collects all matches in a native loop that advances the cursor by the match length. A **zero-width (empty) match** has length 0, so the cursor never advances: the same empty match is found forever and appended to an ever-growing native vector. Any pattern that can match the empty string (`a*`, `b?`, `x{0,3}`, `(a)|`, `(?:)`, …) therefore causes an infinite loop with unbounded memory growth. The call is synchronous native code, so it blocks the entire event loop and cannot be interrupted by `try/catch`, `AbortController`, `--max-old-space-size`, or timers — the process must be killed externally. This diverges from the built-in engine, where `'xxxx'.match(/a*/g)` returns a finite array.

## Root cause

```cpp
// lib/match.cc:44 — global branch of WrappedRE2::Match
while (re2->regexp.Match(str, byteIndex, str.size, anchor, &match, 1)) {
    groups.push_back(match);
    byteIndex = match.data() - str.data + match.size();   // += 0 for a zero-width match
}
```

When `match.size() == 0`, `byteIndex` is unchanged, so the next iteration matches the same empty position again; `groups` grows without bound. The other iteration paths already guard this: `lib/split.cc:50-55` advances by `getUtf8CharSize` on an empty match, and `exec` advances `lastIndex`. Only this global `Match` loop is missing the guard.

## Proof of concept

```js
const RE2 = require('re2');
'x'.match(new RE2('a*', 'g'));   // never returns; grows memory until OOM
// also: 'b?', 'x{0,3}', '(a)|', 'c*d*', '(?:)'; empty subject '' triggers it too
```

Compare with the built-in engine, which terminates:

```js
'xxxx'.match(/a*/g);   // -> ["", "", "", "", ""]
```

Measured on a clean `npm install re2@1.25.1` (latest), stock prebuilt binary: resident memory grew **~550 MB → 2.3 GB in ~3 seconds** at 100% CPU, and the process had to be `SIGKILL`ed externally.

## Impact

Denial of service. Reachable remotely and without authentication wherever an application runs a **global** `RE2` through `String.prototype.match` and either the pattern or the subject is attacker-influenced — e.g. a user-supplied regular expression, or a fixed empty-matchable pattern applied to user input. Because the loop blocks the event loop and exhausts memory in seconds, a single request can wedge a worker and, via memory exhaustion, affect the whole host.

## Suggested fix

Mirror the empty-match handling already present in `split.cc`: when the match is zero-width, advance the cursor by one code point.

```cpp
// lib/match.cc, inside the global while-loop
groups.push_back(match);
size_t off = match.data() - str.data;
if (match.size()) {
    byteIndex = off + match.size();
} else {
    byteIndex = off + (off < str.size ? getUtf8CharSize(str.data[off]) : 1);
}
```

## Resolution

Fixed in re2 1.25.2.

The global match loop in `lib/match.cc` now advances the cursor by one Unicode
code point when a match is zero-width, so a pattern that can match the empty
string terminates with a finite result identical to the built-in engine
(`'xxxx'.match(/a*/g)` returns five empty strings). This mirrors the guard
already present in `split`.

**Remediation:** upgrade to `re2@1.25.2` or later.

**Workaround** (if you cannot upgrade): do not run a global `RE2` through
`String.prototype.match` when the pattern is attacker-influenced or can match
the empty string. Iterate with `matchAll`/`exec`, or use the non-global form;
both already advanced the cursor correctly.

## References
- https://github.com/uhop/node-re2/security/advisories/GHSA-6hxr-mr5r-9836
- https://nvd.nist.gov/vuln/detail/CVE-2026-68499
- https://github.com/uhop/node-re2/commit/56293de4fc0914d7bc35f92e98de25b0d9bb417d
- https://github.com/uhop/node-re2
- https://github.com/uhop/node-re2/releases/tag/1.25.2
