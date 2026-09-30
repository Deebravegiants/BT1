# [M] DexManagerFacet: batchRemoveDex

## Summary
Severity: Medium
Contest weight: 0.6739
Dataset id: 2226
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[DexManagerFacet.sol#L71-L73](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/DexManagerFacet.sol#L71-L73)  

The function intends to allow the removal of multiple dexes approved for swaps. However, the function will only remove the first DEX because `return` is used instead of `break` in the inner for loop.

```solidity
if (s.dexs[j] == _dexs[i]) {
    _removeDex(j);
    // should be replaced with break;
    return;
}
```

This error is likely to have gone unnoticed because no event is emitted when a DEX is added or removed.

## Proof of Concept
Add the following lines below [L44 of](https://github.com/code-423n4/2022-03-Li.finance/blob/main/test/facets/AnyswapFacet.test.ts#L44) `[AnyswapFacet.test.ts](https://github.com/code-423n4/2022-03-lifinance/blob/main/test/facets/AnyswapFacet.test.ts#L44)`

```solidity
await dexMgr.addDex(ANYSWAP_ROUTER)
await dexMgr.batchRemoveDex([ANYSWAP_ROUTER, UNISWAP_ADDRESS])
// UNISWAP_ADDRESS remains as approved dex when it should have been removed
console.log(await dexMgr.approvedDexs())
```

## Recommendation
Replace `return` with `break`.

```solidity
if (s.dexs[j] == _dexs[i]) {
    _removeDex(j);
    break;
}
```

In addition, it is recommend to emit an event whenever a DEX is added or removed.

Fixed in lifinance/lifi-contracts@0a078bbbdf8ec92bd72efc4257900af416d537d4

Valid POC and sponsor confirmed with fix.
