# [M] Unattributed pushed-transaction verification failures allow sustained batch-verification poisoning of block processing

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CWE: Asymmetric Resource Consumption (Amplification), Allocation of Resources Without Limits or Throttling
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-g7c4-2w6c-cr3r
Type: github-advisory

## Details
# Unattributed pushed-transaction verification failures allow sustained batch-verification poisoning of block processing

| Field | Value |
|---|---|
| Severity | Moderate |
| CVSS 3.1 | AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (5.3) |
| CWE | CWE-770 (Allocation of Resources Without Limits or Throttling) / CWE-405 (Asymmetric Resource Consumption) |
| Affected versions | v6.0.0-rc.0 and v6.0.0 (the attribution behaviour was introduced with the GHSA-m9xx-8rcj-vmgp changes) |
| Patched versions | 6.1.0 |
| Reporter credit | Partner disclosure (@ebfull and @ValarDragon ) |
| Fix PR | [#10995 ](https://github.com/ZcashFoundation/zebra/pull/10995) |

## Am I affected?

You are affected if you run an affected version with default peer-to-peer networking. The condition is reachable by any peer that can connect and push transactions; no authentication or special privileges are required, and the default configuration is affected. The impact is degraded block-processing performance (the reporter measures roughly a sevenfold slowdown under full Orchard load) sustained for as long as the attack continues, because the sending peer is never penalised. There is no crash, no consensus divergence, and no state corruption.

## Summary

When a directly-pushed mempool transaction fails verification, Zebra does not record the sending peer's address on the failure, so the peer is never misbehavior-scored and never banned, even though the address was available. Because Orchard proof verification runs through a process-global batch verifier that is shared between mempool transaction verification and block verification, a peer can repeatedly push transactions carrying invalid Orchard proofs at no cost. Each invalid proof that enters a shared batch causes the batch to fail, forcing Zebra to re-verify every proof in that batch individually (the slow path), including honest proofs from block processing that were batched alongside. The result is a sustained, unattributed degradation of block verification driven by cheap unauthenticated peer traffic.

## Details

Verified on v6.0.0 (identical on v6.0.0-rc.0).

Attribution gap. `download_if_needed_and_verify` receives the sending peer as `source: Option<SocketAddr>` (`zebrad/src/components/mempool/downloads.rs:326`) and uses it for the per-peer admission cap. In the gossip match, the downloaded-by-id branch retains the network-supplied advertiser, but the directly-pushed branch discards the source:

```rust
Gossip::Tx(tx) => {
    metrics::counter!("mempool.pushed.transactions.total", ...).increment(1);
    (tx, None)                       // downloads.rs:432
}
```

The verification error is then wrapped as `Invalid { error, advertiser_addr }` (downloads.rs:457), so for a pushed transaction `advertiser_addr` is `None`. Misbehavior scoring is applied only when the error carries an address, so a directly-pushed invalid transaction is rejected and cached but the sending peer is never scored and never banned. The GHSA-m9xx-8rcj-vmgp change restored the source for admission accounting but not for this verification-failure scoring path.

Shared batch verifier. Orchard (halo2) proofs are verified through per-era process-global verifiers (`zebra-consensus/src/primitives/halo2.rs:259` onward), each built as a `Fallback` over a batch verifier (halo2.rs:239-240). Mempool transaction verification and block transaction verification both route Orchard proofs through the same per-era verifier. When a batch fails, the `Fallback` re-runs every item in that batch individually (halo2.rs:196-198). Batch verification amortises cost across proofs; individual verification does not, so one invalid proof forces every proof batched with it onto the slow path.

Amplification. Because the pushing peer is never banned, an attacker can sustain a stream of transactions bearing invalid Orchard proofs from a single unauthenticated connection. Those invalid proofs enter the shared batch, cause repeated batch failures, and drive the fallback-to-individual path for honest block-processing proofs that share the batch, degrading block verification for the duration of the attack. The reporter measures roughly a sevenfold block-processing slowdown under full Orchard load.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-g7c4-2w6c-cr3r_
