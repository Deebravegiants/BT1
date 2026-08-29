# [?] cl: GLOAS audit fixes — clone aliasing, PTC consistency, memory leaks, nil panics (#21248)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-05-21
Source: https://github.com/erigontech/erigon/commit/93480e4c0f2d3060efff4ca18ece948f860e3804
Type: security-commit

## Details
cl: GLOAS audit fixes — clone aliasing, PTC consistency, memory leaks, nil panics (#21248)

## Summary

- **Fix PTC consistency bug in `notifyPtcMessages`**: old code used two
different states (`s` vs `blockState`) for PTC computation, causing
validators to be mapped to wrong PTC positions. Now uses
`blockState.GetPTCFromWindow` consistently and iterates aggregation bits
directly, eliminating the intermediate `GetIndexedPayloadAttestation`
allocation and sort.
- **Fix `ExecutionPayloadEnvelope.Clone()` shallow copy**: old Clone
shared `Payload` and `ExecutionRequests` pointers (aliasing). Now
deep-copies via SSZ roundtrip. Also fixes `NewExecutionPayloadEnvelope`
to use `GloasVersion` instead of `BellatrixVersion`.
- **Add nil-panic guards** in `ProcessExecutionPayloadBid`,
`verifyExecutionPayloadBidSignature`, and
`ProcessExecutionPayloadEnvelope` for malformed SSZ inputs.
- **Cap `pendingELPayloads` at 1024** to prevent unbounded growth;
`DrainPendingELPayloads` now reuses backing array when small, releases
to GC when large.
- **Clean up `blockTimeliness` sync.Map** in `onNewFinalized` (was
growing without bound).
- **Switch gossip topic scoring from `strings.Contains` to exact `==`
match**, removing fragile ordering dependency between
`execution_payload` and `execution_payload_bid`.

No pre-GLOAS behavior changes — all fixes are in GLOAS-specific code
paths or produce identical results for pre-GLOAS topics.

## Test plan

- [x] `TestSignedExecutionPayloadEnvelopeCloneNilMessage` — nil Message
Clone
- [x] `TestGetPTCFromWindow` /
`TestGetPTCFromWindowRejectsSlotOutsideWindow` — PTC window accessor
- [x] `TestPendingELPayloadsDropOldestAtCap` /
`TestDrainPendingELPayloadsReleasesLargeBackingArray` — cap limit and
drain

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/93480e4c0f2d3060efff4ca18ece948f860e3804_
