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
```

_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-78pp-mc9g-g4mw_
