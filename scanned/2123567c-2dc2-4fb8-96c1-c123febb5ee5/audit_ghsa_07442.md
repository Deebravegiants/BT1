# [H] node-tar: Uncontrolled recursion in mapHas/filesFilter allows uncatchable stack-overflow DoS via crafted long-path tar with member selection

## Summary
Severity: High
Advisory: GHSA-r292-9mhp-454m
CVE: CVE-2026-73566
CWE: CWE-400, CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-r292-9mhp-454m
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.21

## Details
## Summary
`node-tar` (npm `tar`) contains an uncontrolled-recursion stack-exhaustion DoS in the internal `mapHas` helper used by `filesFilter`. When a consumer calls `tar.t(...)` or `tar.x(...)` with a non-empty member-selection list, node-tar installs a filter that closes over the recursive `mapHas` (`src/list.ts:33-44`). `mapHas` walks an entry path upward one `path.dirname()` call per recursion **with no segment cap**. A single crafted tar with a GNU-`L` (or PAX-`x`) long-path header can deliver a path of tens of thousands of `/`-separated segments (up to `maxMetaEntrySize` = 1 MiB). The recursion overflows the call stack, throwing an uncatchable `RangeError` that terminates the Node process on async/streaming consumers.

## Root Cause
`filesFilter` (`src/list.ts:27-51`) is installed whenever a caller passes a member-selection list (`src/list.ts:119-122`, `src/extract.ts:55-57`). Its filter is invoked at `src/parse.ts:253` (`entry.ignore = entry.ignore || !this.filter(entry.path, entry)`) inside `Parser[CONSUMEHEADER]` — and crucially **outside** the only try/catch in that method (which wraps `new Header` at `src/parse.ts:179-183`). `mapHas` recurses once per path segment with no depth limit. The `Unpack` `maxDepth` guard (`src/unpack.ts:342`, in `[CHECKPATH]`) only runs on the `'entry'` event, which fires *after* `CONSUMEHEADER` has already invoked the filter — so the stack overflows before any depth guard executes. `tar.t` (list) has no `maxDepth` at all.

## Impact
Unauthenticated, remotely-triggerable denial of service: a ~188-byte gzip (≈26 KB tar) crashes any service that lists or extracts *selected members* from an untrusted archive (package registries, CI artifact/cache restore, upload processors). On async (`await tar.t(...)`/`tar.x(...)`) and streaming/`pipe` consumers the `RangeError` escapes the promise as an `uncaughtException` and terminates the process — standard defensive `try/catch` around the async call does NOT prevent it. (The synchronous API is catchable; the async/stream paths — the dominant server pattern — are not.)

## Proof of Concept
```js
// Build a tar whose single entry has a GNU-L long path of ~12,000 "a/" segments (~26 KB),
// gzip it (≈188 bytes), then have a consumer list/extract with member selection:
const tar = require('tar');
await tar.t({ file: 'evil.tar.gz', gzip: true }, ['some-member']); // -> RangeError, process exit
```
Empirically reproduced on Node v24.18.0 against built `dist/commonjs` of node-tar 7.5.20: 188-byte gzip → 26,112-byte tar (12,000 segments) → uncaught `RangeError: Maximum call stack size exceeded` → process exit. A control run with no member-selection list (filter not installed) parses cleanly (exit 0), isolating `mapHas` as the sole cause.

## Attack Chain
1. **Entry.** Attacker crafts a tar with a GNU `L` (or PAX `x`) long-path header whose body is `"a/"`×~12000 (~26 KB), followed by a normal file entry.
   - **Guard:** `maxMetaEntrySize` caps the meta body at 1 MiB (`src/parse.ts:241`).
   - **Bypass proof:** 26 KB ≪ 1 MiB → accepted (verified: 26 KB archive parsed up to the filter).
2. **Trigger.** Victim service calls `tar.t({file},[sel])` or `tar.x({file,cwd},[sel])` (member selection — a documented, common API).
   - **Guard:** `Unpack.maxDepth` (default 1024) at `src/unpack.ts:342`; decompression-ratio guard.
   - **Bypass proof:** `maxDepth` lives in `[CHECKPATH]` on the `'entry'` event, which fires *after* `CONSUMEHEADER`'s filter call — the crash occurs before it (extract exits 1 with default maxDepth). `tar.t` has no maxDepth. Ratio is ~139× (trivial); no total-bytes cap applies to the uncompressed meta body.
3. **Sink.** `this.filter(entry.path)` → `mapHas` recurses once per `/` segment (`src/list.ts:39`).
   - **Guard:** try/catch in `CONSUMEHEADER`.
   - **Bypass proof:** the only try/catch wraps `new Header` (`src/parse.ts:179-183`); the `this.filter(...)` call at `src/parse.ts:253` is outside it. The `RangeError` propagates out of the stream write/`'data'` path → uncaught exception (verified: `process.on('uncaughtException')` fires; async `await`+`try/catch` does NOT intercept).
4. **Impact.** Node process termination; a 188-byte gzip crashes any consumer that lists/extracts selected members from untrusted archives.

## Bypass Evidence
- `mapHas` recursion is member-name-independent: the crash fires even when the requested members do not match the malicious entry path — the attacker only needs the consumer to *use* member selection.
- Standalone `mapHas` overflows at 20k–30k segments; on the real streaming path (atop `write → CONSUMECHUNK → CONSUMEHEADER → filter`) it crashes at ≤8k segments (finder's ~12k estimate is accurate for the reachable path).
- Control (no member list → no filter) parses cleanly (exit 0), isolating `mapHas`.

## Affected Versions
`<= 7.5.20` (npm `tar`). `mapHas` present verbatim on tag `v7.5.20` (latest GitHub release and npm `dist-tag latest`); no segment/depth cap in `src/list.ts` or the `CONSUMEHEADER` filter path; HEAD == 7.5.20, no unreleased fix.

## Suggested Fix
Rewrite `mapHas` iteratively (walk `dirname` in a `while` loop with a segment/visited cap), or enforce a hard path-segment limit in `Header`/`Parser` independent of `maxMetaEntrySize`, applied before any per-entry filter runs.

## Dedup Note
Distinct from CVE-2024-28863 / GHSA-f5x3-32g6-qm9j "lack of folders depth validation" (that bounds `mkdir` recursion during *extraction* via `maxDepth` in `Unpack[CHECKPATH]` on the `'entry'` event — a different sink, code path, and fix; runs after the filter and does not apply to `tar.t`). Also distinct from the PAX NUL/numeric-path crash advisories (improper-input-to-fs / type confusion, not recursion) and the gzip-bomb advisory (resource exhaustion on disk writes). None touch `list.ts`/`filesFilter`/`mapHas` or require member selection.

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-r292-9mhp-454m
- https://nvd.nist.gov/vuln/detail/CVE-2026-73566
- https://github.com/isaacs/node-tar/commit/631ae59121bf8fc8a22bbae35f074cb9b789cd4a
- https://github.com/isaacs/node-tar
- https://github.com/isaacs/node-tar/releases/tag/v7.5.21
