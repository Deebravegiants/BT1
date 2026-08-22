# [H] Peer-Advertised Mempool Transactions Can Stall Tokio Workers via Synchronous Transparent Script FFI Before Policy Rejection

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-13
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-84j3-rw4c-gqmj
Type: github-advisory

## Details
## Am I affected?

You are affected if you run an affected version with default peer-to-peer networking. The condition is reachable by any peer that can connect and send transactions; no authentication or special privileges are required, and the default configuration is affected. 

## Summary

When Zebra verifies a transaction offered by a peer for the mempool, it runs full script verification (a synchronous C++ FFI call, `CachedFfiTransaction::is_valid()`) on a Tokio worker thread before applying the cheap mempool policy checks that would reject a non-standard, high-signature-operation P2SH script. Because the FFI call is synchronous, the worker polling it is blocked for the duration and cannot be preempted by Tokio or Tower timeouts. Concurrent script verification is bounded by a shared buffer of width 5, so a peer sending cheap-to-produce transactions that require expensive script verification can occupy that verification capacity, degrading the responsiveness of mempool and block verification for the duration of the load.

## Details

Verified on v5.2.0.

In the transaction verifier (`zebra-consensus/src/transaction.rs`), the mempool branch (`req.is_mempool()`, `:514`) constructs the `CachedFfiTransaction` (`:520`), then builds and awaits the asynchronous check set that includes script verification:

```rust
// zebra-consensus/src/transaction.rs:578
async_checks.check().await?;
// ...
// :607 - the sigop count is only computed AFTER script verification has run
let sigops = tx.sigops()?;
```

The signature-operation count, and therefore any standardness decision that depends on it, is computed only after the script verification has already run (`:607`, with `cached_ffi_transaction.p2sh_sigops()` used at `:619` and `:632`). There is no cheap standardness gate ahead of the script FFI: on v5.2.0 there is no `MAX_P2SH_SIGOPS` (or equivalent standardness rejection) in the transaction checks, so a non-standard high-sigop P2SH transaction reaches full script verification before any policy check could reject it.

Two concurrency bounds govern the blast radius:

- `VERIFIER_BUFFER_BOUND = 5` (`zebra-consensus/src/router.rs:61`, applied at `:355` and `:385`): the transaction verifier and router are each buffered at width 5, shared across mempool, block sync, and inbound block verification. At most about five script FFI verifications run concurrently.
- `MAX_INBOUND_CONCURRENCY_PER_PEER = 5` (`zebrad/src/components/mempool/downloads.rs:116`): the per-peer download cap introduced by GHSA-4fc2-h7jh-287c. This applies to the `Inv`/`QueueFromPeer` advertisement path. Directly pushed transactions (`PushTransaction`) route through `Queue` with no peer source and are not bounded by this per-peer cap (tracked separately as GHSA-m9xx-8rcj-vmgp), so a single peer can drive these verifications against the shared verifier buffer and the global queue (`MAX_INBOUND_CONCURRENCY = 500`, `mempool/downloads.rs:106`).

Because the FFI call is synchronous, a worker blocked inside it cannot be preempted by the async runtime's timeouts, so the occupancy is not shed by ordinary backpressure until the verification completes. Misbehavior scoring for script-verification failures is applied only after the call returns, not while the worker is occupied.

## Impact

**High severity**. A remote, unauthenticated peer can submit transactions that are cheap to generate but expensive to verify, causing Zebra to perform synchronous CachedFfiTransaction::is_valid() script verification on Tokio worker threads before inexpensive mempool standardness checks reject them. Because the FFI call blocks the async runtime, verification cannot be preempted or timed out once it begins.

Under sustained load, attacker-controlled script verification can occupy runtime workers and prevent honest transaction verification, block verification, mempool processing, peer networking, RPC handling, and timers from making forward progress, rendering the node effectively unresponsive for the duration of the attack. 

## Patches

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-84j3-rw4c-gqmj_
