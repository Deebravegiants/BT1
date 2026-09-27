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
        return Err(MempoolError::FullQueue);
    }
}
```

Because direct tx messages arrive with source = None, they are not counted against the sender's per-peer budget; only the global cap remains. This is the direct-push counterpart of the advertisement-path issue fixed in GHSA-4fc2-h7jh-287c: the per-peer cap introduced there covers advertised transaction IDs but not directly pushed transactions.

## Patches

Recommended fix shape: preserve the connected peer's address for directly pushed transactions and route them through the same per-peer admission accounting used for advertised transactions (the QueueFromPeer path), so any candidate originating from a remote peer consumes that peer's per-peer budget before consuming the global queue. The peer's transient address is already available where the tx message is handled. Retain source = None only for genuinely local or internally generated candidates. Consider enforcing per-peer accounting at the single point all peer-originated candidates converge, so a future entry point cannot reopen the same gap. Upgrade to 6.0.0-rc.0 or later once available.

## Workarounds

There is no configuration-only workaround that preserves normal operation. To reduce exposure before upgrading, operators can run without accepting inbound P2P connections, or restrict inbound peers to trusted hosts, at the cost of reduced connectivity.

## Impact

A remote peer that completes the standard handshake (no authentication, default configuration) can send many unique direct tx messages and hold more than its intended five concurrent admission slots. Honest peers' transaction gossip can be delayed or dropped while the attacker holds slots, and the node spends CPU and memory on attacker-supplied transaction verification. The global cap (MAX_INBOUND_CONCURRENCY = 500) continues to bound total in-flight work, so this does not cause unbounded growth, a persistent halt, a crash, or any consensus effect. There is no confidentiality or integrity impact. The impact is limited to availability and relay degradation of the inbound mempool path, which recovers as queue slots drain.

## Credit

Reported by Yi Wang (yi.wang@invariant.email), with a clear write-up and a working proof-of-concept unit test.

## References

- Related advisory: GHSA-4fc2-h7jh-287c (per-peer mempool admission cap; advertisement path)
- CWE-770: Allocation of Resources Without Limits or Throttling
