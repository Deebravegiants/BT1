# [M] zcashd Normalizes Malformed V4 Sapling valueBalance Encodings That Zebra Rejects

## Summary
Severity: Medium
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-08
Source: https://github.com/zcash/zcash/security/advisories/GHSA-3jg6-49c6-q99v
Type: github-advisory

## Details
# `zcashd` Normalizes Malformed V4 Sapling `valueBalance` Encodings That `Zebra` Rejects

### Summary
A malformed V4 Sapling transaction encoding with `nSpendsSapling = 0`, `nOutputsSapling = 0`, and a non-zero serialized `valueBalanceSapling` is accepted by `zcashd` after normalization to an empty Sapling bundle, while `Zebra` rejects the same raw bytes during deserialization. This is a real consensus parsing mismatch, but it is materially narrower than the other reports because the malformed encoding is not preserved through the ordinary stock `zcashd` mempool / mining path.

The practical trigger requires a miner or custom raw block producer that embeds the malformed raw transaction bytes directly into a block. Ordinary `zcashd` relay and mining canonicalize the malformed encoding before block production.

### Details
Validated code revisions used during analysis:

- `zcashd`: `2c63e9aa08cb170b0feb374161bea94720c3e1f5`
- `Zebra`: `a905fa19e3a91c7b4ead331e2709e6dec5db12cb`

`zcashd` side:

- In the V4 read path, `zcashd` parses Sapling fields using `SaplingV4Reader` and decides whether a Sapling bundle exists using `saplingReader.HaveActions()`: [`zcash/src/primitives/transaction.h`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/primitives/transaction.h#L857-L887), [`zcash/src/rust/src/sapling.rs`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/rust/src/sapling.rs#L277-L307).
- Bundle presence depends only on the Sapling spend / output vectors, not on the parsed `valueBalanceSapling`.
- If both vectors are empty, no Sapling bundle is assembled; the exposed `GetValueBalanceSapling()` value is then effectively the normalized empty-bundle value `0`: [`zcash/src/primitives/transaction.h`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/primitives/transaction.h#L701-L705), [`zcash/src/rust/src/sapling.rs`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/rust/src/sapling.rs#L228-L233).
- The later non-contextual rule that would reject `valueBalanceSapling != 0` with no Sapling spends or outputs therefore never fires, because it sees the normalized transaction object rather than the original wire bytes: [`zcash/src/main.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/main.cpp#L1540-L1549).
- `zcashd` also hashes the normalized in-memory transaction object, not the original malformed bytes: [`zcash/src/primitives/transaction.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/primitives/transaction.cpp#L136-L146).

`Zebra` side:

- `Zebra`'s V4 transaction parser reads `valueBalanceSapling`, Sapling spends, and Sapling outputs, then explicitly errors if both vectors are empty and `value_balance != 0`: [`zebra/zebra-chain/src/transaction/serialize.rs`](https://github.com/ZcashFoundation/zebra/blob/a905fa19e3a91c7b4ead331e2709e6dec5db12cb/zebra-chain/src/transaction/serialize.rs#L874-L910).
- When `Zebra` receives a block from the network, it reparses the raw block bytes and therefore sees the malformed encoding again: [`zebra/zebra-network/src/protocol/external/codec.rs`](https://github.com/ZcashFoundation/zebra/blob/a905fa19e3a91c7b4ead331e2709e6dec5db12cb/zebra-network/src/protocol/external/codec.rs#L655-L657), [`zebra/zebra-chain/src/block/serialize.rs`](https://github.com/ZcashFoundation/zebra/blob/a905fa19e3a91c7b4ead331e2709e6dec5db12cb/zebra-chain/src/block/serialize.rs#L149-L162).

Why the practical path is narrow:

- `zcashd` ordinary transaction relay first deserializes raw bytes into `CTransaction` and only then calls `AcceptToMemoryPool()`: [`zcash/src/main.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/main.cpp#L7516-L7539).
- Mempool entries store the parsed transaction object, not the original malformed raw bytes: [`zcash/src/txmempool.h`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/txmempool.h#L56-L88).
- Stock `zcashd` mining inserts those normalized transaction objects into candidate blocks: [`zcash/src/miner.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/miner.cpp#L604-L606), [`zcash/src/primitives/block.h`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/primitives/block.h#L109-L112).
- Even after block reception, accepted malformed raw blocks can be re-emitted in canonical form on subsequent `zcashd` relay hops because `zcashd` serializes the parsed `CBlock` object again: [`zcash/src/main.cpp`](https://github.com/zcash/zcash/blob/2c63e9aa08cb170b0feb374161bea94720c3e1f5/src/main.cpp#L2200-L2218).

### PoC
Validated commits:

- `zcashd`: `2c63e9aa08cb170b0feb374161bea94720c3e1f5`
- `Zebra`: `a905fa19e3a91c7b4ead331e2709e6dec5db12cb`

_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-3jg6-49c6-q99v_
