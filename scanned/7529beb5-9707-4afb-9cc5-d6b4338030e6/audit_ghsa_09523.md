# [H] iskorotkov/avro: CPU Exhaustion in Decoder

## Summary
Severity: High
Advisory: GHSA-w8j3-pq8g-8m7w
CVE: CVE-2026-46385
CWE: CWE-1284, CWE-400, CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-w8j3-pq8g-8m7w
Type: github-advisory

## Affected
- Go: `github.com/iskorotkov/avro/v2` — affected >=0 <2.33.0

## Details
# CPU Exhaustion in Avro Decoder via Unbounded Block-Count Iteration

## Summary

The Avro array and map decoders looped over an attacker-controlled block-count value without checking the underlying reader's error state inside the loop body. `Reader.ReadBlockHeader` returns the count as a Go `int`, which is 64-bit on `amd64` / `arm64` targets — so a producer can declare a block of up to `math.MaxInt64` (~9.2 × 10¹⁸) elements followed by EOF (or any truncated payload), and the decoder will attempt that many no-op iterations before propagating the error. The realistic ceiling is "indefinite until the worker is killed externally" — a single hostile payload pins a CPU core until the process is OOM-killed, deadline-cancelled, or terminated. Remote, unauthenticated denial-of-service.

The fix exits the loop on the first inner-decode error. It does not bound the loop length itself; for full coverage on untrusted inputs, also configure `Config.MaxSliceAllocSize` and `Config.MaxMapAllocSize` (the latter introduced in `v2.33.0`).

## Description

Avro arrays and maps are encoded as one or more blocks; each block declares an element count followed by that many encoded elements. The decoder reads the block count as a zigzag-encoded `long`, then iterates that many times calling an inner decoder.

Three iteration sites trusted the block count without checking the reader's accumulated error state between iterations:

- `codec_skip.go` `sliceSkipDecoder.Decode` — skip helper for arrays.
- `codec_skip.go` `mapSkipDecoder.Decode` — skip helper for maps.
- `reader_generic.go` `Reader.ReadArrayCB` and `Reader.ReadMapCB` — callback-based decoders used by generic and unmarshaling code paths.

Because the inner `Decode(nil, r)` call is a no-op when `r` has already errored (it returns immediately without consuming bytes), the loop would run to completion even after the first iteration's EOF. On `amd64` / `arm64`, `Reader.ReadBlockHeader` returns the count as `int` (= `int64`), so the loop bound is whatever the wire payload specified, up to `math.MaxInt64`. A modest 200-million-count payload (well under 2³¹) already burns several seconds; a `math.MaxInt − 2` payload (the value used in the regression test `TestDecoder_ArrayMultiBlockExceedsMaxInt` from PR #9) effectively pins the goroutine until external kill.

This overlaps with [`GHSA-mc57-h6j3-3hmv`](https://github.com/iskorotkov/avro/security/advisories/GHSA-mc57-h6j3-3hmv): the same large-block-count payload that drives the unbounded loop here also drives the cumulative-arithmetic overflow there (cross-platform), and on a 32-bit target additionally triggers the union-index / byte-slice narrowing.

## Affected components

| File | Function | PR | Fix commit |
|------|----------|----|------------|
| `codec_skip.go` | `sliceSkipDecoder.Decode` | — | [`b124caa`](https://github.com/iskorotkov/avro/commit/b124caa58a821f68f100d86f045f9753b88881e8) |
| `codec_skip.go` | `mapSkipDecoder.Decode` | — | [`b124caa`](https://github.com/iskorotkov/avro/commit/b124caa58a821f68f100d86f045f9753b88881e8) |
| `reader_generic.go` | `Reader.ReadArrayCB` | [#4](https://github.com/iskorotkov/avro/pull/4) | [`2ce4242`](https://github.com/iskorotkov/avro/commit/2ce4242e6095d93470ab3b37ed6082b0596f325c) |
| `reader_generic.go` | `Reader.ReadMapCB` | [#4](https://github.com/iskorotkov/avro/pull/4) | [`2ce4242`](https://github.com/iskorotkov/avro/commit/2ce4242e6095d93470ab3b37ed6082b0596f325c) |

These are the audited and patched sites. Any other code path that iterates over an attacker-controlled count while calling a `Reader`-style decoder is structurally susceptible to the same pattern; reviewers of consumer code should grep for `for range l` / `for i := 0; i < int(l); i++` near `Reader` method calls and confirm an in-loop error check.

## Technical details

**Vulnerable pattern:**

```go
for range l {
    d.decoder.Decode(nil, r)
    // r.Error may have been set by Decode; loop continues regardless.
}
```

After `r.Error != nil`, subsequent `Decode` calls short-circuit and return without consuming bytes or doing useful work, but the loop control variable still runs to `l`. With `l = math.MaxInt64`, the loop body executes ~9.2 × 10¹⁸ times — effectively infinite for any realistic timeout.

**Fixed pattern** ([`b124caa`](https://github.com/iskorotkov/avro/commit/b124caa58a821f68f100d86f045f9753b88881e8), [`2ce4242`](https://github.com/iskorotkov/avro/commit/2ce4242e6095d93470ab3b37ed6082b0596f325c)):

```go
for range l {
    d.decoder.Decode(nil, r)
    if r.Error != nil {
        break
    }
}
```

The fix terminates the loop on the first inner error. It does **not** bound `l` itself — a well-formed payload that actually contains `N` encoded `null` elements still iterates `N` times. The `MaxSliceAllocSize` / `MaxMapAllocSize` caps are the policy-level bound on that case (see Mitigation).

## Fixed behavior

The reader's accumulated error is checked after every inner `Decode` in the four affected loops. Decoder errors now surface in O(1) iterations instead of O(blockCount) when the underlying read fails mid-stream.

## Affected versions

- `github.com/hamba/avro/v2` — all versions up to and including `v2.31.0` (repository is read-only upstream).
- `github.com/iskorotkov/avro/v2` — all versions prior to `v2.33.0`.

## Fixed versions

`github.com/iskorotkov/avro/v2` `v2.33.0` and later. There is no upstream fix for `github.com/hamba/avro/v2` — module path is archived. Migrate to the fork as described under Mitigation.

## Mitigation

Migrate from `github.com/hamba/avro/v2` to `github.com/iskorotkov/avro/v2 >= v2.33.0`. Replace the import path and run `go mod tidy`:

```bash
go get github.com/iskorotkov/avro/v2@latest
```

Or, for consumers that prefer the original import path, a `replace` directive in `go.mod`:

```
replace github.com/hamba/avro/v2 => github.com/iskorotkov/avro/v2 v2.33.0
```

`replace` is honoured only for the **main** module of a build — transitive consumers must add their own `replace`, or migrate the import path directly.

The error-propagation fix runs on the existing decode path and requires no configuration.

For defense-in-depth against well-formed but oversized payloads (where the fix above does not help, because no error fires), set explicit allocation caps:

```go
cfg := avro.Config{
    MaxByteSliceSize:  102_400,
    MaxSliceAllocSize: 10_000,
    MaxMapAllocSize:   10_000,
}.Freeze()

decoder := cfg.NewDecoder(schema, reader)
```

`MaxMapAllocSize` is new in `v2.33.0` and opt-in (default zero, which leaves the previous unbounded behavior). Without setting it, a producer that ships a `math.MaxInt64`-count block still consumes the corresponding memory and CPU; see [`GHSA-mx64-mj3q-7prj`](https://github.com/iskorotkov/avro/security/advisories/GHSA-mx64-mj3q-7prj) for the cumulative-allocation enforcement details.

If you cannot upgrade immediately, the structural workarounds are application-level: per-request decode timeouts, isolated decoder workers under CPU quotas, and rejection of payloads whose advertised block count exceeds a known sane bound for your schema.

## Proof-of-concept input

A minimal payload that triggers the bug for an array of `int`:

```
zigzag-encoded long: math.MaxInt64   (block element count)
EOF                                  (no further bytes)
```

The decoder reads the block-count header, enters the loop, fails to read the first element (EOF), records the error, and then iterates `math.MaxInt64 − 1` further times calling the inner decoder as a no-op. Wall-clock cost on commodity hardware: indefinite — the goroutine pins one CPU core until the process is OOM-killed, deadline-cancelled, or terminated externally. The classic *"a few seconds per request"* characterisation applies only to small-but-still-pathological block counts in the 10⁸–10⁹ range (e.g. `200_999_000` in `TestDecoder_SkipArrayEOF`); the architectural ceiling is `math.MaxInt64`.

A negative block count (`-N`) is also legal in Avro (signals an N-element block with an explicit byte length); the same iteration pattern applies once the count is negated.

## References

- Fix PR: [iskorotkov/avro#4](https://github.com/iskorotkov/avro/pull/4) (callback path)
- Fix commits: [`b124caa`](https://github.com/iskorotkov/avro/commit/b124caa58a821f68f100d86f045f9753b88881e8) (skip helpers), [`2ce4242`](https://github.com/iskorotkov/avro/commit/2ce4242e6095d93470ab3b37ed6082b0596f325c) (callback path)
- Release: [`v2.33.0`](https://github.com/iskorotkov/avro/releases/tag/v2.33.0)
- Security policy: [`SECURITY.md`](https://github.com/iskorotkov/avro/blob/main/SECURITY.md)
- Related advisories on this fork: [`GHSA-mc57-h6j3-3hmv`](https://github.com/iskorotkov/avro/security/advisories/GHSA-mc57-h6j3-3hmv) (integer overflow — same large-block-count payload also triggers cumulative-arithmetic overflow there), [`GHSA-mx64-mj3q-7prj`](https://github.com/iskorotkov/avro/security/advisories/GHSA-mx64-mj3q-7prj) (unbounded map allocation — the policy-level bound on well-formed huge inputs)
- Cross-module precedent on `hamba/avro`: [`GO-2023-1930`](https://pkg.go.dev/vuln/GO-2023-1930) / `CVE-2023-37475` / `GHSA-9x44-9pgq-cf45`
- Upstream (read-only): [`hamba/avro`](https://github.com/hamba/avro)

## Credits

- **Discovery and fixes** (commits `b124caa` skip helpers and `2ce4242` callback path, PR #4): Daniel Błażewicz ([@klajok](https://github.com/klajok))
- **Release authorship**: Ivan Korotkov ([@iskorotkov](https://github.com/iskorotkov))

## Timeline

- **2026-04-28** — Skip-decoder fix (`b124caa`) merged.
- **2026-04-30** — Callback-decoder fix (PR #4, `2ce4242`) merged.
- **2026-05-06** — `v2.33.0` tagged and released.
- **2026-05-11** — Advisory published.
- **2026-05-15** — Advisory revised.

## References
- https://github.com/iskorotkov/avro/security/advisories/GHSA-w8j3-pq8g-8m7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-46385
- https://github.com/iskorotkov/avro
