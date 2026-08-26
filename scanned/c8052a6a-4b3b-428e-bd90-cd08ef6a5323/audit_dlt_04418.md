# [M] MultiHop swap is implemented incorrectly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/2
Type: sherlock-finding

## Details
csanuragjain

medium

# MultiHop swap is implemented incorrectly

## Summary
If `canBatchSwap` is called with `swaps.length=1` then ideally multihop should revert mentioning an invalid swap. But due to incorrect implementation of `isMultiHopSwap`, contract will find user data eligible for multi hop swap

## Vulnerability Detail
1. User call `canCall` function with `sig` as `BATCH_SWAP`
2. This makes call to `canBatchSwap` function
3. Lets say User call this with only 1 value in swap in calldata, which makes swaps.length=1

```solidity
(
            ,
            IVault.BatchSwapStep[] memory swaps,
            IAsset[] memory assets,
            ,
            ,
        ) = abi.decode(data, (
                uint8, IVault.BatchSwapStep[], IAsset[], IVault.FundManagement, uint256[], uint256
            )
        );
```

4. `isMultiHopSwap` is now called which instantly returns true since swap.length=1 and loop runs for swaps.length-1 which is 0 times in this case

```solidity
function isMultiHopSwap(IVault.BatchSwapStep[] memory swaps)
        internal
        pure
        returns (bool)
    {
        uint steps = swaps.length;
        for (uint i; i < steps - 1; i++) {
            if (swaps[i].assetOutIndex != swaps[i+1].assetInIndex)
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/2_
