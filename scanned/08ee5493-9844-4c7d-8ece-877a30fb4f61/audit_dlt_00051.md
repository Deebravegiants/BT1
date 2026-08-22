# [M] Direct P2P tx messages bypass per-peer mempool admission accounting

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-03
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-m9xx-8rcj-vmgp
Type: github-advisory

## Details
## Am I affected?

You are affected if all of these hold:
- You run an affected zebrad version (>= 5.0.0, before 6.0.0-rc.0).
- Your node accepts inbound P2P connections.
- Your node is close enough to the chain tip that the mempool is enabled.

You are at reduced risk or unaffected if your node does not accept inbound connections, is firewalled to trusted peers, or is not near the chain tip.

## Summary

A remote peer can occupy more than its intended share of Zebra's inbound mempool admission capacity by sending transactions as direct P2P tx messages instead of transaction-ID advertisements. Direct tx messages enter the mempool download and verification queue without preserving the sending peer as the source, so the per-peer admission cap does not apply. A single inbound peer can crowd out honest peers' transaction relay. The global queue cap still bounds total in-flight work, so this is a per-peer fairness bypass, not unbounded resource exhaustion. Operators running publicly reachable, near-tip nodes should upgrade to the patched release once available.

## Details

Zebra enforces a per-peer cap on concurrent inbound mempool admissions (MAX_INBOUND_CONCURRENCY_PER_PEER = 5) alongside a global cap (MAX_INBOUND_CONCURRENCY = 500). The per-peer cap is enforced only when the candidate transaction carries a peer source.

Two inbound transaction paths exist. The advertisement path (inv / AdvertiseTransactionIds) carries the announcing peer's address and routes the request with a peer source, so the per-peer cap applies; this path was addressed by GHSA-4fc2-h7jh-287c. The direct-push path (Message::Tx) converts a directly received full transaction to an internal push request that does not carry the peer address, and queues it without a source.

In the direct-push path, the peer address is dropped at message handling:

```rust
Message::Tx(ref transaction) => Request::PushTransaction(transaction.clone()).into(),
```

The push request is queued generically, with no source:

```rust
PushTransaction(transaction) =>
    mempool.oneshot(mempool::Request::Queue(vec![transaction.into()]))
```

It reaches the downloader with source = None, and the per-peer cap is checked only when a source is present:

```rust
if let Some(source) = source {
    let count = self.pending_per_peer.get(&source).copied().unwrap_or(0);
    if count >= MAX_INBOUND_CONCURRENCY_PER_PEER {
```

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-m9xx-8rcj-vmgp_
