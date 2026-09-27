# [H] iskorotkov/avro: Denial-of-Service Vulnerability in Decoder

## Summary
Severity: High
Advisory: GHSA-mx64-mj3q-7prj
CWE: CWE-1284, CWE-400, CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-mx64-mj3q-7prj
Type: github-advisory

## Affected
- Go: `github.com/iskorotkov/avro/v2` — affected >=0 <2.33.0

## Details
# Memory Exhaustion via Unbounded Map Allocations in Avro Decoder

## Summary

The Avro map decoder accepted attacker-controlled block-element counts from the wire format and grew the destination map without enforcing an upper bound. The slice decoder already had `Config.MaxSliceAllocSize` for the equivalent attack against arrays; the map decoder had no analogous limit, so a producer could declare an arbitrarily large map (in one block, or chunked across many sub-limit blocks) and exhaust process memory until the OOM killer fired.

The fix introduces `Config.MaxMapAllocSize` with cumulative enforcement across block boundaries. **The new limit is opt-in**: the field defaults to zero, which preserves the previous unbounded behavior for backward compatibility. **Upgrading to `v2.33.0` alone does not mitigate the issue** — consumers of untrusted Avro data must explicitly set `MaxMapAllocSize` on their `avro.Config`.

## Description

Avro maps are encoded as a sequence of blocks; each block declares a `long` element count followed by that many key/value pairs. The decoder uses these counts both to size the destination map and as the loop bound for reading entries.

Pre-fix, the map decoder enforced no upper limit at any layer:

- No per-block element-count check.
- No cumulative across-block element-count check.
- No memory-budget check before `make(map[...]..., n)` or before growing the map.

The slice decoder had been hardened via `Config.MaxSliceAllocSize` and tracked cumulatively across blocks; the map decoder was a missing-by-symmetry gap. Even a partial per-block bound on maps would have been insufficient on its own — Avro permits encoding a logical map as many small blocks, so a producer could split a 10 GB map into 10,000 sub-MaxMapAllocSize blocks and still drive total allocation past any single-block threshold. The fix tracks cumulative entry count at block-header boundaries — *before* the block's entries are decoded into the map — and errors out before allocation when the running total would exceed the configured cap.

Two decoder variants were affected, both in `codec_map.go`:

- `mapDecoder.Decode` — string-keyed maps.
- `mapDecoderUnmarshaler.Decode` — `encoding.TextUnmarshaler`-keyed maps (e.g. `map[CustomKey]V` where `*CustomKey` implements `UnmarshalText`).

## Affected components

| File | Symbol | Pre-fix behavior | Post-fix behavior |
|------|--------|------------------|-------------------|
| `config.go` | `Config.MaxMapAllocSize` | Field did not exist | New `int` field; default zero means unlimited (back-compat) |
| `codec_map.go` | `mapDecoder.Decode` | Read block count, grew map unbounded | Validates cumulative count against `MaxMapAllocSize` at each block header |
| `codec_map.go` | `mapDecoderUnmarshaler.Decode` | Same | Same |

PR [#5](https://github.com/iskorotkov/avro/pull/5) (`fix/map-alloc-chunking-bypass`) covers both decoders and adds chunking-attack tests for both. The same PR also adds the previously-missing chunking-attack test coverage for the slice path in `534c7518` — the slice *logic* was already correct, only its test coverage was incomplete.

## Technical details

The fix mirrors the slice decoder's pattern:

1. At each block header, read the element count as `int64`.
2. Add it to a running total maintained across the block loop.
3. If the running total exceeds `Config.MaxMapAllocSize` (when nonzero), return an error before allocating any of that block's entries.
4. Otherwise, decode the block's entries into the map.

Per-block enforcement alone would be bypassable by chunking; cumulative tracking closes that. The check sits at the block-header read, *before* per-entry allocation, so a single oversized block also cannot allocate first and then fail post-hoc.

`Config.MaxMapAllocSize` semantics match `Config.MaxSliceAllocSize`: zero means unlimited, any positive value is the cumulative cap on element count (not byte size).

## Fixed behavior

`v2.33.0` adds the `MaxMapAllocSize` configuration field and the cumulative-enforcement logic in both map decoders. Both decoders return a descriptive error when the cumulative entry count would exceed the configured cap; no entries are allocated past the limit.

Tests added in PR #5 cover, for both `mapDecoder` and `mapDecoderUnmarshaler`:

- Single-block allocation exceeding the limit (rejected before allocation).
- Chunking attack: multiple sub-limit blocks whose cumulative count exceeds the limit (rejected at the block-header that crosses the threshold).
- Multi-block under the limit (decoded normally).

## Affected versions

- `github.com/hamba/avro/v2` — all versions up to and including `v2.31.0` (repository is read-only upstream).
- `github.com/iskorotkov/avro/v2` — all versions prior to `v2.33.0`. Note: `v2.33.0` and later are vulnerable *by default* and only protected when `MaxMapAllocSize` is explicitly configured — see Mitigation.

## Fixed versions

`github.com/iskorotkov/avro/v2` `v2.33.0` and later, **with `Config.MaxMapAllocSize` explicitly set to a non-zero value**.

A bare upgrade to `v2.33.0` without setting `MaxMapAllocSize` leaves the decoder in the same unbounded state as `v2.32.0`. This is a backward-compatibility choice; a future major version may flip the default. Until then, treat this advisory as requiring both an upgrade *and* a configuration change.

There is no upstream fix for `github.com/hamba/avro/v2` — module path is archived. Migrate to the fork as described under Mitigation.

## Mitigation

Migrate from `github.com/hamba/avro/v2` to `github.com/iskorotkov/avro/v2 >= v2.33.0` **and** configure an allocation cap appropriate for your schema. The recommended approach for processes that decode untrusted input is a dedicated frozen config, used at every relevant call site, rather than mutating `avro.DefaultConfig`:

```go
cfg := avro.Config{
    MaxByteSliceSize:  102_400,
    MaxSliceAllocSize: 10_000,
    MaxMapAllocSize:   10_000,
}.Freeze()

decoder := cfg.NewDecoder(schema, reader)
```

Choose the values based on the largest legitimate map your schema produces; a value 2–10× that ceiling provides headroom for benign variance while still bounding worst-case memory.

For consumers that prefer the original import path, a `replace` directive in `go.mod` is supported:

```
replace github.com/hamba/avro/v2 => github.com/iskorotkov/avro/v2 v2.33.0
```

`replace` is honoured only for the **main** module of a build — transitive consumers must add their own `replace`, or migrate the import path directly.

If you cannot upgrade immediately, the only structural workarounds are out-of-band: run decoders in memory-constrained child processes or cgroups so an OOM is contained, reject inputs from sources without resource controls, and apply per-request decode deadlines so a runaway decode at least times out before the OOM killer fires.

## Proof-of-concept input

Two attack shapes, both targeting `map[string]int`:

**Single-block, oversize block count.** Emit one block header declaring `n = 2³¹ − 1` (or any value whose `n × averageEntrySize` exceeds available memory) followed by truncated entries. Pre-fix, the decoder pre-allocates `make(map[string]int, n)`, which fails or stalls long before EOF is reached.

**Chunking bypass.** Emit `k` blocks each declaring `n / k` elements, with `n / k` below any plausible per-block threshold but `n` itself well into the GB range. Pre-fix, the decoder happily grows the map block-by-block until the OS kills the process. Post-fix with `MaxMapAllocSize = 10_000`, the decoder rejects whichever block-header read pushes cumulative count past 10,000.

Either shape can be produced by hand-crafting the wire bytes; no `iskorotkov/avro` writer is needed to generate them.

## References

- Fix PR: [iskorotkov/avro#5](https://github.com/iskorotkov/avro/pull/5)
- Fix commit: [`5192df9`](https://github.com/iskorotkov/avro/commit/5192df96a158999344ac96ebcb1f7461d626f6d7) (`codec_map.go`, `config.go`, tests)
- Slice-path chunking-attack test coverage added in the same PR: [`534c7518`](https://github.com/iskorotkov/avro/commit/534c7518152a893d8b4dea962669bd1123308a00)
- Release: [`v2.33.0`](https://github.com/iskorotkov/avro/releases/tag/v2.33.0)
- Security policy: [`SECURITY.md`](https://github.com/iskorotkov/avro/blob/main/SECURITY.md)
- Related advisories on this fork: [`GHSA-mc57-h6j3-3hmv`](https://github.com/iskorotkov/avro/security/advisories/GHSA-mc57-h6j3-3hmv) (integer overflow), [`GHSA-w8j3-pq8g-8m7w`](https://github.com/iskorotkov/avro/security/advisories/GHSA-w8j3-pq8g-8m7w) (CPU exhaustion — the same chunked-payload shape may trigger both before allocation pressure kicks in)
- Cross-module precedent on `hamba/avro`: [`GO-2023-1930`](https://pkg.go.dev/vuln/GO-2023-1930) / `CVE-2023-37475` / `GHSA-9x44-9pgq-cf45`
- Upstream (read-only): [`hamba/avro`](https://github.com/hamba/avro)

## Credits

- **Fix author** (commit `5192df9`, PR #5 — `MaxMapAllocSize` config field, cumulative enforcement in both map decoders, chunking-attack tests for slices and maps): Ivan Korotkov ([@iskorotkov](https://github.com/iskorotkov))
- **Review** (commit `a5fbddcb`, "address review comments"): Daniel Błażewicz ([@klajok](https://github.com/klajok))

## Timeline

- **2026-04-30** — `MaxMapAllocSize` introduced (`5192df9`); chunking-attack test coverage for slices added (`534c7518`).
- **2026-05-01** — PR #5 merged into `main`.
- **2026-05-06** — `v2.33.0` tagged and released.
- **2026-05-07** — Advisory published.
- **2026-05-15** — Advisory revised.

## References
- https://github.com/iskorotkov/avro/security/advisories/GHSA-mx64-mj3q-7prj
- https://github.com/iskorotkov/avro
