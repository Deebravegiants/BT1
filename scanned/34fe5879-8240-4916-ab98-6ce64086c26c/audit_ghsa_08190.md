# [H] iskorotkov/avro: Integer Overflow in Decoder

## Summary
Severity: High
Advisory: GHSA-mc57-h6j3-3hmv
CVE: CVE-2026-46384
CWE: CWE-1284, CWE-190, CWE-191, CWE-681
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-mc57-h6j3-3hmv
Type: github-advisory

## Affected
- Go: `github.com/iskorotkov/avro/v2` — affected >=0 <2.33.0

## Details
# Integer Overflow in Avro Decoder

## Summary

Several Avro decoder paths read attacker-controlled 64-bit values from the wire format and either narrowed them to platform-sized `int` before bounds-checking, or summed them with overflow-prone signed-`int` arithmetic. On 32-bit targets (`GOARCH=386`, `arm`, `mips`, `wasm`, etc.), the truncation paths can silently bypass byte-slice limits, select the wrong union branch, or hit the OCF negative-`make` panic via wrap. Three sub-issues are not 32-bit-specific: cumulative-size arithmetic overflow in `arrayDecoder.Decode` / `mapDecoder.Decode` / `mapDecoderUnmarshaler.Decode` (wraps at `math.MaxInt64` on amd64 / arm64 and bypasses `MaxSliceAllocSize` / `MaxMapAllocSize`), `math.MinInt` negation in block-header handling, and `make([]byte, size)` with a negative size in OCF block reads — all three panic or bypass caps on any platform, giving an attacker a denial-of-service primitive there.

Exploitation requires only an untrusted Avro stream. No primitives reach beyond denial-of-service on current code paths; see the union-index discussion below for a caveat.


## Description

Six call sites in the decoder accepted `int64` values from the Avro wire format and converted to `int` before validation. On a 32-bit build any wire value with magnitude `≥ 2³¹` truncates and the post-conversion value bears no useful relationship to the original. A value of `(1<<32) + 5` narrows to `5`; `1<<32` narrows to `0`; values just past `MaxInt32` narrow to large negatives.

This is distinct from the existing `Config.MaxSliceAllocSize`, `Config.MaxByteSliceSize`, and the new `Config.MaxMapAllocSize` limits, because narrowing happens *before* the limit comparison — the limit sees the truncated value, not the original wire value, so the cap is bypassed.

Three further sub-issues are not 32-bit-specific:

- `arrayDecoder.Decode`, `mapDecoder.Decode`, and `mapDecoderUnmarshaler.Decode` summed attacker-controlled block lengths via `size += int(l)` and then checked `size > limit`. On amd64 / arm64 the running total wraps at `math.MaxInt64`; the post-wrap negative value passes the `> limit` check, and the decoder proceeds. Regression test: `TestDecoder_ArrayMultiBlockExceedsMaxInt` uses `math.MaxInt − 2` for the second block's count and a `MaxSliceAllocSize` of 13 to demonstrate this on amd64. The Avro block-count field is a signed `long` on the wire, so block counts up to `math.MaxInt64` are admissible — there is no implicit 2³¹ ceiling.
- `ReadBlockHeader()` returns the absolute value of negative block lengths; the negation is unsafe for `math.MinInt`, which on every platform panics on overflow.
- `ocf/ocf.go readBlock()` passes the decoded block size directly to `make([]byte, size)`. A negative wire value panics on every platform; on 32-bit, values `> MaxInt32` additionally panic via the narrowing path.

## Affected components

| File | Function(s) | Bug class | Platforms |
|------|-------------|-----------|-----------|
| `reader.go` | `ReadBlockHeader` — narrowing | Narrowing | 32-bit |
| `reader.go` | `ReadBlockHeader` — `-math.MinInt` | Signed overflow (CWE-191) | all |
| `reader.go` | `readBytes` (via `Reader.ReadBytes`, `Reader.ReadString`) | Narrowing | 32-bit |
| `reader_skip.go` | `SkipString`, `SkipBytes` (and OCF skip path) | Narrowing | 32-bit |
| `codec_array.go` | `arrayDecoder.Decode` | Cumulative-size arithmetic overflow (CWE-190) | all |
| `codec_map.go` | `mapDecoder.Decode`, `mapDecoderUnmarshaler.Decode` | Cumulative-size arithmetic overflow (CWE-190) | all |
| `ocf/ocf.go` | `skipToEnd`, `readBlock` — narrowing | Narrowing | 32-bit |
| `ocf/ocf.go` | `readBlock` — negative `make([]byte, …)` | Unchecked-negative (CWE-1284) | all |
| `reader_generic.go` | union-type index decoding in `Reader.ReadNext` | Narrowing, possible wrong-branch selection | 32-bit |

PR #9 (commit [`bed99b3`](https://github.com/iskorotkov/avro/commit/bed99b315ec097a1a5eb7ae074ef57a91848c583)) covered `ReadBlockHeader`, the cumulative checks in array/map codecs, and the skip helpers. The completeness pass (commit [`e1a570f`](https://github.com/iskorotkov/avro/commit/e1a570f9a8a4fe4b1bc2b4b1fb6d24e4a5f04358)) covered the union index, `readBytes`, and OCF `readBlock`, and added a 32-bit CI job.

Note: the typed-codec union decoder in `codec_union.go` (`getUnionSchema` → `Reader.ReadInt`) is **not** affected by the union-index narrowing — `ReadInt` returns `int32`, no narrowing occurs. The narrowing is specific to `Reader.ReadNext` in the generic decode path (reached via `Unmarshal` into `any` / `map[string]any`).

## Technical details

1. **Block-header narrowing and `MinInt` negation.** `ReadBlockHeader()` returned wire-format `int64` values through narrower operations; on 32-bit, large positives truncated. Negating `math.MinInt` to convert a negative block-count signal into a positive size is undefined-on-overflow, and on every platform `-MinInt` panics on overflow when used in subsequent arithmetic. The fix reads into a `*64`-suffixed local, range-checks against `MinInt32`/`MaxInt32` (or `MinInt`/`MaxInt` as appropriate), and narrows after validation.

2. **Cumulative array and map size overflow (all platforms).** `arrayDecoder.Decode`, `mapDecoder.Decode`, and `mapDecoderUnmarshaler.Decode` summed attacker-controlled block lengths using overflow-prone addition; cumulative size could wrap before reaching the configured limit. On amd64 with `MaxSliceAllocSize = 13`, block 1 of 3 elements, block 2 of `math.MaxInt − 2` elements: the pre-fix `size += int(l)` wraps to `math.MinInt`, then `MinInt > 13` is false, so the check passes and the decoder proceeds. The fix uses subtraction-safe comparisons (`l > limit - size` rather than `size + l > limit`), which is overflow-immune.

3. **Skip-length truncation.** `SkipString`, `SkipBytes`, and the OCF skip helper now route through `SkipNBytesInt64()`, which keeps the length as `int64` and range-checks before any narrowing.

4. **Byte-slice length truncation.** A wire-format length such as `(1<<32) + 5` truncated to `5` in `readBytes()`, slipping past `Config.MaxByteSliceSize` on 32-bit. The fix reads the length as `int64`, compares against `MaxByteSliceSize` before narrowing, and returns "value is too big" if exceeded.

5. **Union index narrowing (generic decode path only).** `Reader.ReadNext` decoded the union index as `int64` and immediately cast to `int`. On 32-bit, `1<<32` narrowed to `0` and silently selected `types[0]` despite the explicit upper-bound check immediately above. If `types[0]` is the null branch (idiomatic for `["null", T]` nullable unions), the practical result is a null value where the producer encoded a non-null payload — a DoS-grade logic error. If `types[0]` is a non-trivial schema, downstream bytes are parsed against the wrong schema and produce well-typed but semantically wrong values; treat this as the worst-case interpretation when assessing impact on your own deployment. The typed-codec union decoder (`codec_union.go` `getUnionSchema` → `Reader.ReadInt`) is not affected.

6. **OCF block-size narrowing and negative `make`.** `readBlock()` passes the decoded `int64` size directly to `make([]byte, size)`. A negative wire value panics on every platform; a value `> MaxInt32` additionally panics via the 32-bit narrowing path. The fix validates the size is in `[0, MaxByteSliceSize]` before narrowing.

## Fixed behavior

Both commits apply the same pattern across every site:

1. Read the wire value into an `int64`-typed local.
2. Range-check upper and lower bounds before narrowing.
3. Compare cumulative limits using subtraction-safe arithmetic.
4. Route skip operations through `SkipNBytesInt64()`.
5. Return descriptive errors using the consistent `"value is too big"` / `"value is too small"` wording.
6. Cast to `int` only after validation succeeds.

CI: a `test-386` job runs the suite under `GOARCH=386` with `CGO_ENABLED=0` (`-race` is amd64/arm64-only). Three tests with untyped `2147483648` constants whose `t.Skipf` gates fire too late (the file fails to compile before any test runs) were split into sibling `*_64bit_test.go` files gated by `//go:build amd64 || arm64 || ...`.

## Affected versions

- `github.com/hamba/avro/v2` — all versions up to and including `v2.31.0` (repository is read-only upstream).
- `github.com/iskorotkov/avro/v2` — all versions prior to `v2.33.0`.

## Fixed versions

`github.com/iskorotkov/avro/v2` `v2.33.0` and later. There is no upstream fix for `github.com/hamba/avro/v2` — module path is archived. Migrate to the fork as described under Mitigation.

## Mitigation

Migrate from `github.com/hamba/avro/v2` to `github.com/iskorotkov/avro/v2 >= v2.33.0`. The packages share the same API surface; replace the import path and run `go mod tidy`:

```diff
- import "github.com/hamba/avro/v2"
+ import "github.com/iskorotkov/avro/v2"
```

For consumers that prefer the original import path, a `replace` directive in `go.mod` is supported:

```
replace github.com/hamba/avro/v2 => github.com/iskorotkov/avro/v2 v2.33.0
```

`replace` is honoured only for the **main** module of a build — transitive consumers must add their own `replace`, or migrate the import path directly.

No further configuration is required to benefit from the integer-narrowing fixes — the validation runs on the existing decode path.

If you cannot upgrade immediately:

- Do not decode untrusted Avro data on any platform — the cumulative-arithmetic overflow paths (`arrayDecoder.Decode`, `mapDecoder.Decode`, `mapDecoderUnmarshaler.Decode`) are reachable on amd64 / arm64. The truncation paths on 32-bit cannot be mitigated by setting `Config.MaxByteSliceSize` lower, because the truncated post-narrowing value is what the limit sees, not the original wire value.
- For the cross-platform `math.MinInt` and OCF negative-size panic paths, wrapping `Decode` / OCF read calls in a goroutine with `defer recover()` contains the crash, but is not a substitute for upgrading. The other narrowing paths return errors rather than panicking, so `recover()` does nothing for them.
- Isolate decoding workers so a crash is bounded.

## Proof-of-concept inputs

- A `bytes` or `string` length of `(1<<32) + N` for small `N`, which narrows to `N` on 32-bit and bypasses `Config.MaxByteSliceSize`.
- A union index of `1<<32`, which narrows to `0` on 32-bit and selects `types[0]` despite the upper-bound check.
- An array or map encoded across multiple blocks whose cumulative element count wraps the signed `int` running total before the limit check fires. Demonstrated on amd64 by `TestDecoder_ArrayMultiBlockExceedsMaxInt`: `MaxSliceAllocSize = 13`, block 1 of `3`, block 2 of `math.MaxInt − 2`. Wraps to `math.MinInt`, check passes, decoder proceeds.
- A block header whose absolute value is `math.MinInt`, triggering the unsafe negation (cross-platform).
- An OCF block size that is negative on the wire, causing `make([]byte, size)` to panic (cross-platform); or a positive value `> MaxInt32` on 32-bit, same outcome via narrowing.

## References

- Initial hardening PR: [iskorotkov/avro#9](https://github.com/iskorotkov/avro/pull/9)
- Completeness pass PR: [iskorotkov/avro#10](https://github.com/iskorotkov/avro/pull/10)
- Fix commits: [`bed99b3`](https://github.com/iskorotkov/avro/commit/bed99b315ec097a1a5eb7ae074ef57a91848c583), [`e1a570f`](https://github.com/iskorotkov/avro/commit/e1a570f9a8a4fe4b1bc2b4b1fb6d24e4a5f04358)
- Release: [`v2.33.0`](https://github.com/iskorotkov/avro/releases/tag/v2.33.0)
- Security policy: [`SECURITY.md`](https://github.com/iskorotkov/avro/blob/main/SECURITY.md)
- Related advisories on this fork: [`GHSA-w8j3-pq8g-8m7w`](https://github.com/iskorotkov/avro/security/advisories/GHSA-w8j3-pq8g-8m7w) (CPU exhaustion — overlaps via the same large-block-count payload shape), [`GHSA-mx64-mj3q-7prj`](https://github.com/iskorotkov/avro/security/advisories/GHSA-mx64-mj3q-7prj) (unbounded map allocation)
- Cross-module precedent on `hamba/avro`: [`GO-2023-1930`](https://pkg.go.dev/vuln/GO-2023-1930) / `CVE-2023-37475` / `GHSA-9x44-9pgq-cf45`
- Upstream (read-only): [`hamba/avro`](https://github.com/hamba/avro)

## Credits

- **Discovery and initial fixes** (PR #9, commit `bed99b3` — `ReadBlockHeader`, cumulative array/map checks, skip helpers): Daniel Błażewicz ([@klajok](https://github.com/klajok))
- **Completeness fixes** (commit `e1a570f` — union index, `readBytes`, OCF `readBlock`, 32-bit CI coverage): Ivan Korotkov ([@iskorotkov](https://github.com/iskorotkov))

## Timeline

- **2026-05-04** — Initial integer-overflow hardening (PR #9, `bed99b3`) merged.
- **2026-05-04** — Completeness pass (`e1a570f`) merged; 32-bit CI job added.
- **2026-05-06** — `v2.33.0` tagged and released.
- **2026-05-11** — Advisory published.
- **2026-05-15** — Advisory revised.

## References
- https://github.com/iskorotkov/avro/security/advisories/GHSA-mc57-h6j3-3hmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-46384
- https://github.com/iskorotkov/avro
