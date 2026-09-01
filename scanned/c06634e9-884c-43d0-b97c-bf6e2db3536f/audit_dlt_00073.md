# [C] Block Validator Undercounts Coinbase and P2SH Sigops

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-44498
Published: 2026-05-02
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-jv4h-j224-23cc
Type: github-advisory

## Details
Zebra's block validator undercounts transparent signature operations against the 20000-sigop block limit (`MAX_BLOCK_SIGOPS`), allowing it to accept blocks that `zcashd` rejects with `bad-blk-sigops`. A miner who produces such a block can split the network: Zebra nodes follow the offending chain while `zcashd` nodes do not.

Two distinct undercounts:

#### A: Coinbase Hidden Legacy Sigops

`zcashd`'s `GetLegacySigOpCount()` includes the coinbase input's `scriptSig`. Zebra's `Sigops` impl skipped the coinbase input entirely, so up to ~98 sigops (the 100-byte coinbase script length cap, less the height prefix) could be hidden inside the coinbase `scriptSig` without being charged against the block limit.

#### B: Aggregate P2SH Sigops.

`zcashd`'s `GetP2SHSigOpCount()` parses each P2SH input's redeem script with `accurate=true` and sums those sigops into the block-wide total via `ConnectBlock`. The check is per-block, not per-transaction, and the limit applies regardless of who mines the offending block — a miner just needs to include enough P2SH-spending transactions whose redeem scripts together exceed 20000 sigops. Zebra computed P2SH sigops only on the mempool-acceptance path (used for ZIP-317 weighting) and never accumulated them during block validation. A block whose aggregate redeem-script sigops exceed 20000 (e.g. 1334 P2SH spends × 15 sigops = 20010) would be accepted by Zebra and rejected by `zcashd`.

### Patches

Fixed in zebra-script (next release) and Zebra (next release).

### Workarounds

None. Operators relying on Zebra for consensus should upgrade.

### References

- `MAX_BLOCK_SIGOPS` constant inherited from Bitcoin via the Zcash protocol spec's §7.6 catch-all "Other rules inherited from Bitcoin", tracked for explicit documentation in [zcash/zips#568](https://github.com/zcash/zips/issues/568).
- `zcashd` `GetLegacySigOpCount`: <https://github.com/zcash/zcash/blob/v6.11.0/src/main.cpp#L826-L836>
- `zcashd` `GetP2SHSigOpCount`: <https://github.com/zcash/zcash/blob/v6.11.0/src/main.cpp#L840-L852>
- `zcashd` `ConnectBlock` aggregates per-tx sigops and compares against `MAX_BLOCK_SIGOPS`.
