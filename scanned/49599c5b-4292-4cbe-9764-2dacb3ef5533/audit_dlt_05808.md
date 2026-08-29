# [?] Fix resource exhaustion when replaying finalized-block transactions (#12374)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-08-03
Source: https://github.com/paritytech/polkadot-sdk/commit/1407d3feba9d3fc95e20823cd0b74acbe1ca24ee
Type: security-commit

## Details
Fix resource exhaustion when replaying finalized-block transactions (#12374)

## Description

Re-applying a finalized block's transactions can reject with
`ExhaustsResources` some that
originally succeeded, so runtime APIs that replay a block
(`pallet-revive`'s `trace_block` /
`trace_tx`) drop the rejected tail transactions' traces.

**Cause.** Each extrinsic is charged its worst-case `proof_size`;
`StorageWeightReclaim` refunds
the difference down to the actual size read from a proof-size recorder.
Authoring has a recorder
registered, so the over-charge is reclaimed; the replay has none, so
reclaim is skipped,
`proof_size` accumulates past the block limit, and `CheckWeight` rejects
the tail.

**Fix.** Replay the block through the runtime API with a proof-size
recorder registered.

## Integration

- New **unsafe-gated** RPC `state_callRecorded(name, bytes, block)` on
`StateApi`, the recorded
sibling of `state_call`: runs the call re-enacting `block` at its parent
state with a
proof-size recorder, replaying `block`'s stored recording when available
(fresh recorder
otherwise). `bytes` is the opaque SCALE-encoded args — the node doesn't
inspect them, so
versioned payloads work; `block` only locates the parent state and the
recording.
- New `TracingExecuteBlock::call_recorded(block, method, call_data)`
trait method (default impl
errors, non-breaking; implemented for parachains in
`cumulus-client-service`).

_Trimmed to 38 lines — full report: https://github.com/paritytech/polkadot-sdk/commit/1407d3feba9d3fc95e20823cd0b74acbe1ca24ee_
