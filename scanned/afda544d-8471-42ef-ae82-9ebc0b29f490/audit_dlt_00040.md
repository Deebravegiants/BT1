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


_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-rpcw-q5mr-gq35_
