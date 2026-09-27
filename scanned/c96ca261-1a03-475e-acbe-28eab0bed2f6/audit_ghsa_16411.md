# [C] Nervos CKB P2P DoS Attacks

## Summary
Severity: Critical
Advisory: GHSA-84x2-2qv6-qg56
Ecosystem: crates.io
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-84x2-2qv6-qg56
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.34.0

## Details
The P2P protocols lack of rate limit. For example, in relay protocol, when a node receives a broadcasted `tx_hashes`, it will mark it in memory to avoid duplicated requests. [code → ](https://github.com/nervosnetwork/ckb/blob/26e4837212c392c3c706a0da7a056131fb060433/sync/src/relayer/transactions_process.rs#L67).

It is easy to establish a DoS attach by generating random tx hashes.

### Impact

It affects all nodes connected to the P2P network.

### Workarounds

Apply rate limit on the data sent to CKB P2P port.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-84x2-2qv6-qg56
- https://github.com/nervosnetwork/ckb/commit/c5eb5478b635cea2ccef8676cf97692cd38293c3
