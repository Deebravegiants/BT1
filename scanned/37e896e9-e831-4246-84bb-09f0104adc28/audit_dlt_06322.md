# [M] Swap transactions can be pending for long time due to missing deadline causing users fund loss

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-25
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/37
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x9fb374a4c2ae8857ba7b53666ca15ac29b18f58b34b8e4944ea2b1cd8ece19da
**Severity:** medium

**Description:**
**Description**\

`CatalystVaultVolatile.localSwap()` can be used to swap between two assets within the vault. 


```solidity
    function localSwap(
        address fromAsset,
        address toAsset,
        uint256 amount,
        uint256 minOut
    ) nonReentrant external override returns (uint256) {

 . . . some code

        // Calculate the return value.
        uint256 out = calcLocalSwap(fromAsset, toAsset, amount - fee);

        // Ensure the return value is more than the minimum output.
        if (minOut > out) revert ReturnInsufficient(out, minOut);


 . . . some code

    }
```

While swapping, it takes care of slippage issue with argument `minOut`, However, it lacks the deadline check in swap function.

Catalyst is a cross-chain AMM, facilitating cross-chain swaps and today most of the AMMs provide users with an option to limit the execution of their pending actions, such as swaps, adding liquidity, etc with deadline as an argument. 

One of the example is [Uniswap V2](https://github.com/Uniswap/v2-periphery/blob/0335e8f7e1bd1e8d8329fd300aea2ef2f36dd19f/contracts/UniswapV2Router02.sol#L229-L230) where it provides deadline as an argument which checks and ensures the transaction is expired after end of deadline, Therefore such transactions can not be kept as pending by miners.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/37_
