# [H] zcashd repeatedly persists the same invalid pool-delta block without caching it as invalid

## Summary
Severity: High
Chain: Zcash
Component: zcash/zcash
CWE: Uncontrolled Resource Consumption
Published: 2026-07-13
Source: https://github.com/zcash/zcash/security/advisories/GHSA-78pp-mc9g-g4mw
Type: github-advisory

## Details
# zcashd repeatedly persists the same invalid pool-delta block without caching it as invalid

Suggested severity: Medium / Moderate

Affected versions: confirmed on current `zcash/zcash` master `db3082b` (post-v6.12.3 hotfix merge, 2026-05-11). The v6.12.3 release code still has the same `AcceptBlock` / `ReceivedBlockTransactions` ordering. No patched version is known as of 2026-05-21.

## Summary

`zcashd` writes a received block body to `blk*.dat` before `ReceivedBlockTransactions()` computes and stores aggregate value-pool deltas. If `SetChainPoolValues()` rejects the block because the aggregate per-block pool delta is outside `MoneyDeltaRange`, `ReceivedBlockTransactions()` returns a plain `error()` before setting `BLOCK_HAVE_DATA`, `nTx`, or a failed-block flag.

The block index entry remains header-only, so replaying the same P2P `block` message appends the same invalid block body to disk again. A peer is not rejected or banned because the validation state is not marked invalid.

The initial block requires valid proof-of-work / custom block production. After such a block exists, replay is unauthenticated P2P traffic. This is therefore a resource-exhaustion DoS, not a consensus split or funds/keys/privacy issue.

## Details

Relevant code in `src/main.cpp`:

- `AcceptBlock()` calls `WriteBlockToDisk()` before `ReceivedBlockTransactions()`:

```cpp
if (dbp == NULL) {
    if (!WriteBlockToDisk(block, blockPos, chainparams.MessageStart())) {
        AbortNode(state, "Failed to write block");
    }
}
setDirtyBlockIndex.insert(pindex);
if (!ReceivedBlockTransactions(block, state, chainparams, pindex, blockPos)) {
    return error("AcceptBlock(): ReceivedBlockTransactions failed");
}
```

- `ReceivedBlockTransactions()` calls `SetChainPoolValues()` and returns before marking the block as having data:

```cpp
if (!SetChainPoolValues(chainparams, block, pindexNew)) {
    return error("ReceivedBlockTransactions(): SetChainPoolValues failed");
}

pindexNew->nTx = block.vtx.size();
pindexNew->nFile = pos.nFile;
pindexNew->nDataPos = pos.nPos;
pindexNew->nStatus |= BLOCK_HAVE_DATA;
```

- `ComputePoolDeltas()` accumulates per-block Sprout deltas across all transactions:

```cpp
sproutValue -= js.vpub_new;
if (!MoneyDeltaRange(sproutValue)) {
    return error("%s: sprout value delta out of range: %d at height %d.%s", ...);
}
```

The PoC uses two non-coinbase v4 transactions. Each transaction has one JoinSplit with `vpub_new = MAX_MONEY`, so each transaction individually passes the non-contextual `CheckTransaction()` bounds (`vpub_new > MAX_MONEY` is the rejected case). The block-level aggregate becomes `sproutValue = -2 * MAX_MONEY`, which fails `MoneyDeltaRange()` inside `SetChainPoolValues()`.

At that point the body has already been written to disk, but the index entry has not been marked `BLOCK_HAVE_DATA` or invalid. On the next identical P2P `block` message:

- `fAlreadyHave` is false because `BLOCK_HAVE_DATA` was never set.
- `nTx` is still `0`, so the unrequested-block gate does not treat it as previously processed.
- `BLOCK_FAILED_VALID` is not set.
- The same body is written to `blk*.dat` again.

## PoC

PoC file:

```text
/root/zc/zcash/qa/rpc-tests/p2p_pool_delta_disk_replay.py
```

Run from `/root/zc/zcash`:

```bash
PATH="/root/zc/.tmp-bin:$PATH" CCACHE_DIR="/root/zc/.ccache" python3 qa/rpc-tests/p2p_pool_delta_disk_replay.py --srcdir=./src
```

What the PoC does:

1. Starts a clean regtest `zcashd` node with NU5 active.
2. Builds a valid-PoW block extending the active tip.
3. Adds a large zero-value coinbase output to make disk growth easy to measure while staying under the 2 MB block limit.
4. Adds two v4 JoinSplit transactions that individually pass transaction checks but fail aggregate Sprout pool-delta validation.
5. Recomputes `hashMerkleRoot`, `hashAuthDataRoot`, and `hashBlockCommitments`, then solves the block.
6. Sends the same block 20 times through a direct P2P `block` message.
7. Counts exact serialized copies of that block in `blk*.dat`.

Observed run on current master `db3082b`:

```text
crafted invalid block hash: 044b5b0a8548d3b8a60b0d6579d910cf3a510e81b62b1b6f34ef73b95047b3bb
crafted invalid block size: 903939 bytes
blk*.dat logical size before: 16777216 bytes
blk*.dat logical size after:  33554432 bytes
serialized invalid block copies before: 0
serialized invalid block copies after:  20
Tests successful
```

The test also asserts:

- chain height and best block hash do not advance;
- `getchaintips` reports the crafted block as `headers-only`, not invalid;
- no P2P `reject` message is received by the sender.

## Impact

An attacker who can produce or obtain one valid-PoW block with an invalid aggregate value-pool delta can cause a target `zcashd` node to repeatedly append the same rejected block body to disk. The PoC demonstrates about 904 KB of duplicate block data per replay, with block-file preallocation causing visible logical growth from 16 MiB to 32 MiB after 20 replays.

This can be scaled across repeated P2P deliveries and multiple targets. The sender is not rejected or banned on this path because the failure is returned as a plain error rather than an invalid validation state.

This should be treated as a Medium / Moderate DoS due to the valid-PoW/custom-block-production precondition. It is not a Critical issue because it does not demonstrate funds loss, key compromise, privacy break, consensus split between valid network nodes, or remote code execution.

## Suggested remediation

Avoid leaving a disk-persisted body attached to a header-only, non-invalid index entry after `SetChainPoolValues()` fails. Possible fixes:

- compute per-block pool deltas before `WriteBlockToDisk()` for active-tip blocks;
- mark this failure as an invalid block/body state so the same body cannot be accepted for disk persistence again;
- or reset the persisted body state on this `ReceivedBlockTransactions()` failure path before returning.

The important invariant is that a block body written to disk must not remain replayable indefinitely when the same validation path has already rejected it.
