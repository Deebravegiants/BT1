# [H] Pretext: Algorithmic Complexity (DoS) in the text analysis phase

## Summary
Severity: High
Advisory: GHSA-5478-66c3-rhxr
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-5478-66c3-rhxr
Type: github-advisory

## Affected
- npm: `@chenglou/pretext` — affected >=0 <0.0.5

## Details
`isRepeatedSingleCharRun()` in `src/analysis.ts` (line 285) re-scans the entire accumulated segment on every merge iteration during text analysis, producing O(n²) total work for input consisting of repeated identical punctuation characters. An attacker who controls text passed to `prepare()` can block the main thread for ~20 seconds with 80KB of input (e.g., `"(".repeat(80_000)`).

Tested against commit 9364741d3562fcc65aacc50953e867a5cb9fdb23 (v0.0.4) on Node.js v24.12.0, Windows x64.

A standalone PoC and detailed write-up are attached below.

---

## Root Cause

The `buildMergedSegmentation()` function (line 795) processes text segments produced by `Intl.Segmenter`. When consecutive non-word-like segments consist of the same single character (e.g., `(`, `[`, `!`, `#`), the code merges them into one growing segment (line 859):

```typescript
// analysis.ts:849-859 - the merge branch inside the build loop
} else if (
  isText &&
  !piece.isWordLike &&
  mergedLen > 0 &&
  mergedKinds[mergedLen - 1] === 'text' &&
  piece.text.length === 1 &&
  piece.text !== '-' &&
  piece.text !== '—' &&
  isRepeatedSingleCharRun(mergedTexts[mergedLen - 1]!, piece.text)  // <- O(n) per call
) {
  mergedTexts[mergedLen - 1] += piece.text  // append to accumulator
```

Before each merge, it calls `isRepeatedSingleCharRun()` (line 857) to verify that ALL characters in the accumulated segment match the new character:

```typescript
// analysis.ts:285-291
function isRepeatedSingleCharRun(segment: string, ch: string): boolean {
  if (segment.length === 0) return false
  for (const part of segment) {    // <- Iterates ENTIRE accumulated string
    if (part !== ch) return false
  }
  return true
}
```

`Intl.Segmenter` with `granularity: 'word'` produces individual non-word segments for each punctuation character. For a string of N identical punctuation characters, the merge check is called N times. On the k-th call, the accumulated segment is k characters long, so `isRepeatedSingleCharRun` performs k comparisons.

Total work: `1 + 2 + 3 + ... + N = N(N+1)/2 = O(n^2)`

### Call chain

```
prepare(text, font)                                          // layout.ts:472
  -> prepareInternal(text, font, ...)                        // layout.ts:424
    -> analyzeText(text, profile, whiteSpace='normal')       // layout.ts:430 -> analysis.ts:993
      -> buildMergedSegmentation(normalized, profile, ...)   // analysis.ts:1013 -> analysis.ts:795
        -> for each Intl.Segmenter segment:
          -> isRepeatedSingleCharRun(accumulated, newChar)   // line 857 -> line 285
            -> iterates entire accumulated string            // O(k) per call, k growing
```

## Proof of Concept

The simplest payload is a string of repeated `(` characters:

```typescript
import { prepare } from '@chenglou/pretext'

// 80,000 characters -> ~20 seconds of main-thread blocking
const payload = '('.repeat(80_000)
prepare(payload, '16px Arial')  // Blocks for ~20 seconds
```

Any single character that meets these criteria works:
1. Classified as `'text'` by `classifySegmentBreakChar` (analysis.ts:321) - i.e., not a space, NBSP, ZWSP, soft-hyphen, tab, or newline
2. Produced as individual non-word segments by `Intl.Segmenter` (word granularity)
3. Not `-` or em-dash (explicitly excluded at lines 855-856)

Working payload characters include: `(`, `[`, `{`, `#`, `@`, `!`, `%`, `^`, `~`, `<`, `>`, etc.

---

## Impact

- **Chat/messaging applications:** User sends an 80KB message of `(` characters;
  the receiving client's UI thread freezes for ~20 seconds while rendering.
- **Comment/form systems:** User-supplied text in any text field that uses
  `pretext` for layout measurement blocks the main thread.
- **Server-side rendering:** If `prepare()` is called server-side (Node.js/Bun),
  a single request can consume 20+ seconds of CPU time per 80KB of payload.

The attack requires no authentication, special characters, or encoding tricks -
just repeated ASCII punctuation. 80KB is well within typical text input limits.

As an application-level mitigation, callers can cap the length of text passed to
`prepare()` before a library-level fix is available.

## Suggested Fix

Replace the O(n) full-scan verification with O(1) constant-time checks. 
Since the merge only ever appends the same character to an existing repeated-char run, the invariant is maintained structurally:

**Option A - Check only endpoints (O(1)):**
```typescript
function isRepeatedSingleCharRun(segment: string, ch: string): boolean {
  return segment.length > 0 && segment[0] === ch && segment[segment.length - 1] === ch
}
```
This works for the current code because this branch only fires after earlier merge branches (CJK, Myanmar, Arabic) have been skipped, and those branches produce segments that would not start and end with the same ASCII punctuation character. However, the safety relies on an emergent property of the branch ordering and the other merge branches. Future refactors that add new merge branches or reorder the existing ones could silently break the invariant.

**Option B - Track with metadata**
Add a boolean `lastMergeWasSingleCharRun` alongside the accumulator arrays. Set it to `true` when a single-char merge succeeds, `false` when any other merge branch is taken. Check the flag instead of re-scanning the string.

## References
- https://github.com/chenglou/pretext/security/advisories/GHSA-5478-66c3-rhxr
- https://github.com/chenglou/pretext
- https://github.com/chenglou/pretext/releases/tag/v0.0.5
