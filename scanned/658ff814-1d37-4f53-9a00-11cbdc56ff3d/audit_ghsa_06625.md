# [M] re2: Out-of-bounds heap read in `exec`/`test`/`match` via attacker-influenced `lastIndex` on a non-ASCII subject → uncatchable process crash (DoS)

## Summary
Severity: Medium
Advisory: GHSA-ff84-5f28-78qj
CVE: CVE-2026-67550
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-ff84-5f28-78qj
Type: github-advisory

## Affected
- npm: `re2` — affected >=0 <1.25.2

## Details
## Summary

`re2` validates the user-settable `lastIndex` against the subject's **UTF-8 byte length** but then uses it as a **UTF-16 code-unit count** to walk the subject buffer, with no bounds check. For any non-ASCII subject, the byte length is larger than the true character count, so a `lastIndex` between those two values passes validation while pointing past the end of the buffer. The subsequent walk reads out of bounds. With a large subject the read marches into unmapped memory and the process dies with **SIGABRT/SIGSEGV** — an uncatchable crash (`try/catch` cannot stop it), i.e. a denial of service for any worker/process that runs the match. In some cases the out-of-bounds bytes are copied into the returned value (a bounded, best-effort heap information leak).

## Root cause

The subject wrapper stores the UTF-8 **byte** length in `StrVal::length`:

- `lib/addon.cc:200` `auto argLength = utf8Length(s, isolate);` — UTF-8 **byte** count
- `lib/addon.cc:209` `lastStringValue.reset(buffer, argSize, argLength, startFrom, false, isAscii);`

`setIndex` then validates the (UTF-16) `lastIndex` against that byte length and walks the buffer by character count:

```cpp
// lib/addon.cc:229
void StrVal::setIndex(size_t newIndex) {
    isValidIndex = newIndex <= length;   // length == UTF-8 BYTE length, not UTF-16 length
    if (!isValidIndex) { index = newIndex; byteIndex = 0; return; }
    ...
    // addon.cc:263
    byteIndex = index < newIndex
        ? getUtf16PositionByCounter(data, byteIndex, newIndex - index)
        : getUtf16PositionByCounter(data, 0, newIndex);
    index = newIndex;
}
```

`getUtf16PositionByCounter` reads `data[from]` and advances by the UTF-8 char size with **no check of `from` against the buffer size**:

```cpp
// lib/wrapped_re2.h:264
inline size_t getUtf16PositionByCounter(const char *data, size_t from, size_t n) {
    for (; n > 0; --n) {
        size_t s = getUtf8CharSize(data[from]);   // <-- OOB read once `from` passes the buffer end
        from += s;
        if (s == 4 && n >= 2) --n;
    }
    return from;
}
```

`lastIndex` is user-settable to any positive integer (capped only at `>= 0`, no upper bound):

```cpp
// lib/accessors.cc:166
NAN_SETTER(WrappedRE2::SetLastIndex) {
    ...
    int n = value->NumberValue(...).FromMaybe(0);
    re2->lastIndex = n <= 0 ? 0 : n;   // no upper bound relative to the subject
}
```

For an ASCII subject the byte length equals the UTF-16 length, so the guard is correct — this only triggers on non-ASCII subjects. The out-of-bounds read happens inside `prepareArgument` for any `global`/`sticky` regex, reached by `exec`, `test`, `String.prototype.match`, `replace`, and `split`.

## Proof of concept

**Minimal (AddressSanitizer, deterministic OOB read):**

```js
const RE2 = require('re2');
const re = new RE2('a', 'y');   // sticky; 'g' also works
re.lastIndex = 3;               // 3 <= byteLen(4) passes the guard; only 2 real chars exist
re.exec('éé');                  // U+00E9 = 2 bytes each
```

Built with `-fsanitize=address`, this aborts with:

```
ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 1
  #0 getUtf16PositionByCounter   wrapped_re2.h:268
  #1 StrVal::reset               addon.cc:277
  #2 WrappedRE2::prepareArgument addon.cc:209
  #3 WrappedRE2::Exec            exec.cc:17
```

The overflowed region is the subject buffer allocated by `node::Buffer::New` at `addon.cc:205`.

**Real-world impact on the shipped prebuilt binary (no ASAN) — uncatchable crash:**

```js
const RE2 = require('re2');
const s = '中'.repeat(40000000);        // UTF-16 length 40M, UTF-8 bytes 120M
const re = new RE2('a', 'y');
re.lastIndex = Buffer.byteLength(s) - 1; // passes the byte-length guard, far exceeds real char count
re.exec(s);                              // walks into unmapped memory -> SIGSEGV (exit 139)
```

`try { ... } catch (e) {}` around the call does **not** prevent termination — it is a native fault, not a JS exception. Validated on a clean `npm install re2@1.25.1` (latest): stock prebuilt → SIGSEGV; ASAN build → the heap-buffer-overflow read above.

## Impact

- **Denial of service (primary):** an uncatchable native crash that terminates the Node process/worker. Reachable remotely and without authentication wherever an application (a) uses a `global` or `sticky` `RE2`, (b) applies it to a non-ASCII subject, and (c) sets `lastIndex` from attacker-influenced data (e.g. resuming a scan/pagination at a client-supplied offset).
- **Information disclosure (secondary, best-effort):** the out-of-bounds `byteIndex` can cause adjacent heap bytes to be copied into the returned value (e.g. the leading segment of a `replace` result). This is bounded and unreliable — the subject buffer is `calloc`-allocated (zero-filled) and the over-read distance depends on interpreting out-of-bounds bytes as UTF-8 sizes — so it is noted for completeness, not as a dependable primitive.

This is distinct from GHSA-8hcv-x26h-mcgp (the global `replace()` output-amplification abort), which was fixed in 1.25.1. This `lastIndex` out-of-bounds read is a separate defect and remains present in 1.25.1.

## Suggested fix

Two independent hardenings; either closes the crash, both is safest:

1. **Bound the walk** so it can never read past the buffer:

```cpp
inline size_t getUtf16PositionByCounter(const char *data, size_t size, size_t from, size_t n) {
    for (; n > 0 && from < size; --n) {
        size_t s = getUtf8CharSize(data[from]);
        from += s;
        if (s == 4 && n >= 2) --n;
    }
    return from > size ? size : from;
}
```
(thread `size` through the two call sites in `StrVal::setIndex`).

2. **Validate `lastIndex` against the true UTF-16 length**, not the UTF-8 byte length — e.g. store `s->Length()` (UTF-16 units) as the value compared in `isValidIndex = newIndex <= <utf16Length>`, so an out-of-range `lastIndex` takes the existing `!isValidIndex` early-return path.

## Resolution

Fixed in re2 1.25.2.

`lastIndex` is now validated against the subject's UTF-16 length instead of its
UTF-8 byte length (`lib/addon.cc`), so an out-of-range `lastIndex` is rejected
before the buffer is walked. As defense in depth, the code-unit walk
(`getUtf16PositionByCounter` in `lib/wrapped_re2.h`) is now bounded by the
buffer size and can no longer read past the end.

**Remediation:** upgrade to `re2@1.25.2` or later.

**Workaround** (if you cannot upgrade): do not assign `lastIndex` from untrusted
input, or clamp it to the subject's string length (`str.length`) before calling
`exec`/`test`/`match`/`replace`/`split` on a non-ASCII subject.

## References
- https://github.com/uhop/node-re2/security/advisories/GHSA-ff84-5f28-78qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-67550
- https://github.com/uhop/node-re2/commit/56293de4fc0914d7bc35f92e98de25b0d9bb417d
- https://github.com/uhop/node-re2
- https://github.com/uhop/node-re2/releases/tag/1.25.2
