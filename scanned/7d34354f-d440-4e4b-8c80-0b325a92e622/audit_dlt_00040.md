# [M] Auth Data Body Poisoning in NU5+ Block Ingestion

## Summary
Severity: Medium
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-08
Source: https://github.com/zcash/zcash/security/advisories/GHSA-rpcw-q5mr-gq35
Type: github-advisory

## Details
# Auth Data Body Poisoning in NU5+ Block Ingestion

### Summary

In NU5-and-later blocks, `zcashd` can permanently mark a valid block header as invalid if it receives a poisoned block body before the canonical body. An attacker can mutate V5 transaction authorizing data, such as a transparent input signature, without changing the transaction IDs or the block header hash. `zcashd` stores that poisoned body as `BLOCK_HAVE_DATA` before checking the NU5 `hashBlockCommitments` authorizing-data commitment, and later promotes the body mismatch into `BLOCK_FAILED_VALID` for the shared header. After that, the node rejects the valid body for the same block hash as a duplicate invalid header.

This is a high-severity P2P block-body poisoning issue. It does not let an attacker create a valid invalid chain, but it can stall targeted `zcashd` nodes on the canonical chain and require manual recovery. Nodes and services that rely on the poisoned `zcashd` instance, such as exchanges, RPC providers, indexers, and wallet backends, can observe a stale or divergent chain tip.

### Details

NU5+ transaction IDs and authorizing-data commitments are separate. In `zcashd`, `CTransaction::GetHash()` returns the mined transaction ID, while `CTransaction::GetAuthDigest()` returns the authorizing-data commitment:

- [`CTransaction::GetHash()` and `GetAuthDigest()`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/primitives/transaction.h#L653-L664)
- [`CBlock::BuildAuthDataMerkleTree()` uses `tx.GetAuthDigest()` leaves](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/primitives/block.cpp#L54-L66)

This means an attacker can take a valid NU5+ block body and mutate authorizing data in a V5 transaction while preserving the block header and txid Merkle root. For example, flipping one byte in a non-coinbase transparent input signature keeps the V5 txid unchanged, but changes the transaction auth digest. The block still has the same `hashMerkleRoot` and the same block hash, but its body no longer matches the header's `hashBlockCommitments`.

The vulnerable ordering is in `zcashd` block ingestion:

1. `ProcessNewBlock()` calls `AcceptBlock()` and later `ActivateBestChain()`:
   - [`ProcessNewBlock()`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L5858-L5881)
2. `AcceptBlock()` calls `AcceptBlockHeader()` and then `CheckBlock()` / `ContextualCheckBlock()` using a disabled proof verifier:
   - [`AcceptBlock()`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L5771-L5835)
   - [`ProofVerifier::Disabled()` is used before storing the block](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L5802-L5807)
3. If those checks pass, `AcceptBlock()` writes the block to disk and calls `ReceivedBlockTransactions()`:
   - [`WriteBlockToDisk()` then `ReceivedBlockTransactions()`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L5817-L5833)
4. `ReceivedBlockTransactions()` sets `BLOCK_HAVE_DATA` and raises transaction validity before the NU5 auth-data commitment has been checked:
   - [`ReceivedBlockTransactions()` sets `BLOCK_HAVE_DATA`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L5282-L5310)
5. Only later, during `ConnectBlock()`, `zcashd` builds the auth-data Merkle tree and checks `hashBlockCommitments`:
   - [`hashAuthDataRoot = block.BuildAuthDataMerkleTree()`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L3644-L3650)
   - [`bad-block-commitments-hash` check](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L3785-L3797)
6. If `ConnectBlock()` fails, `InvalidBlockFound()` marks the block index entry as `BLOCK_FAILED_VALID` unless the validation state is marked corruption-possible:
   - [`InvalidBlockFound()` sets `BLOCK_FAILED_VALID`](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L2493-L2510)
7. A later valid body for the same block hash is rejected before it can replace the poisoned body, because `AcceptBlockHeader()` treats any known header with `BLOCK_FAILED_MASK` as an invalid duplicate:
   - [`AcceptBlockHeader()` rejects duplicate invalid headers](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/main.cpp#L5715-L5729)

The issue is that a body-data mismatch that is not fully committed by `hashMerkleRoot` is cached as a header validity failure. For NU5+ blocks, `hashMerkleRoot` alone is insufficient to prove that the received serialized body is the body committed by the header; `hashBlockCommitments` must also be checked against the received body's authorizing data before the block body is stored as `BLOCK_HAVE_DATA` or before a failure is cached as `BLOCK_FAILED_VALID`.

Zebra has the safer ordering. It verifies the txid Merkle root, sends transactions through the transaction verifier, and only then constructs and commits a semantically verified block:

- [`zebra-consensus` checks Merkle root and transaction verification before state commit](https://github.com/ZcashFoundation/zebra/blob/f4618c1b5d54ede7bef68f6c5e7a938f55a4bb88/zebra-consensus/src/block.rs#L218-L365)
- [`zebra-state` recomputes `auth_data_root` and validates the NU5 block commitment](https://github.com/ZcashFoundation/zebra/blob/f4618c1b5d54ede7bef68f6c5e7a938f55a4bb88/zebra-state/src/service/check.rs#L184-L219)

As a result, the poisoned body is rejected before it can poison state, and a later valid body with the same header can still be accepted.

### PoC

The issue can be reproduced deterministically with `submitblock`, without relying on a live P2P race. The P2P race is the realistic delivery mechanism; `submitblock` is just a stable way to demonstrate the poisoned-body cache behavior.

Configuration:

1. Run two `zcashd` nodes on a private regtest or custom test network with NU5 active.
2. Ensure both nodes are synced to the same tip before the test block.
3. The victim node must not already have the test block body.

Reproduction steps:

1. Produce or obtain a valid NU5+ block `B_good` containing at least one V5 non-coinbase transaction with authorizing data. A transparent V5 spend is sufficient.
2. Serialize `B_good` as raw block bytes.
3. Create `B_bad` by mutating only authorizing data in one V5 transaction while preserving parseability and byte lengths. For example, flip one byte inside a transparent input DER signature without changing the CompactSize script length or transaction structure.
4. Do not modify the block header, transaction effects, transaction ordering, or any non-authorizing transaction data.
5. Verify locally that:
   - `B_bad.GetHash() == B_good.GetHash()`
   - `B_bad.hashMerkleRoot == B_good.hashMerkleRoot`
   - the mutated transaction's txid is unchanged
   - the mutated transaction's `GetAuthDigest()` differs
6. Submit `B_bad` to the victim `zcashd` first:

   ```bash
   zcash-cli -regtest submitblock "$B_BAD_HEX"
   ```

   Expected behavior: `AcceptBlock()` stores the poisoned body and `ReceivedBlockTransactions()` marks it as `BLOCK_HAVE_DATA`. `ActivateBestChain()` then calls `ConnectBlock()`, which rejects the block with `bad-block-commitments-hash` or an authorization failure. `InvalidBlockFound()` marks the shared block index entry as `BLOCK_FAILED_VALID`.

7. Submit the valid body `B_good` to the same victim node:

   ```bash
   zcash-cli -regtest submitblock "$B_GOOD_HEX"
   ```

   Expected behavior: the valid body is not accepted. The node already has the same header hash marked under `BLOCK_FAILED_MASK`, so duplicate-header handling returns a duplicate-invalid style failure. In RPC terms, `submitblock` exposes this state through its documented duplicate-invalid path:

   - [`submitblock` duplicate-invalid handling](https://github.com/zcash/zcash/blob/840b9ceaf51286cec1576609562b091789aa4468/src/rpc/mining.cpp#L848-L905)

8. Compare against a fresh node that receives `B_good` first. That node accepts the block and advances normally, while the poisoned victim remains unable to accept the canonical block hash without manual recovery.

The same trigger can be delivered over P2P. An attacker connected to a target `zcashd` node races to provide `B_bad` before honest peers deliver `B_good`. The attacker does not need to mine a block; they only need to receive a newly mined NU5+ block quickly, mutate V5 authorizing data while preserving the txid Merkle root, and deliver the poisoned body first.

### Impact

This is a targeted consensus-state poisoning / chain-stall vulnerability in `zcashd`.

An attacker who wins the block-body delivery race against a target `zcashd` node can cause that node to:

- store a poisoned body for a real canonical block hash,
- mark the shared block header as `BLOCK_FAILED_VALID`,
- reject the valid body for the same block hash when it arrives later,
- stop following the canonical chain at that height until manual recovery.

The attack does not require mining hashpower and does not require creating an alternative valid chain. It requires a P2P race against the target node for a newly mined NU5+ block. A single successful race can stall the target because the invalid status is cached against the block header hash, not just against the poisoned body bytes.

Impacted parties include operators of `zcashd` full nodes, exchanges, RPC providers, wallet backends, indexers, and other infrastructure that depends on a targeted `zcashd` instance for chain tip, confirmation, or balance information. A poisoned node may report a stale chain tip or fail to observe transactions confirmed on the canonical chain.

Recommended remediation:

- Before `ReceivedBlockTransactions()` writes block body metadata or sets `BLOCK_HAVE_DATA`, verify the NU5+ `hashBlockCommitments` value against the received body's computed auth-data root.
- Alternatively or additionally, do not mark `BLOCK_FAILED_VALID` for failures that can be caused by uncommitted or insufficiently committed duplicate body data for a known header.
- Treat body/header commitment mismatches as rejectable body data, not as permanent header invalidity, unless all header-committed body commitments have already been verified.
