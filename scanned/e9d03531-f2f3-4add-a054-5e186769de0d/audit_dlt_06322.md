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

The sponsor mentioned, Ethereum would be one the chains where contracts would be deployed. Consider a below scenario where a user can unknowingly perform bad trades due to missing deadline:

1) Alice wants to swap TokenA(fromAsset) for TokenB(toAsset) with 100 as an amount and 99 is minimum amount he must receive from swap. 

2) Alice's transaction is submitted to the mempool, however, Alice chose a transaction fee that is too low for miners to be interested in including her transaction in a block. The transaction stays pending in the mempool for extended periods, which could be minutes, hours, days or even longer.

3) When the average gas fee dropped far enough for Alice's transaction to become interesting again for miners to include it, her swap will be executed. In the meantime, the price of TokenB could have drastically changed. She will still at least get 99 TokenB due to `minOut`, but it is there might be TokenA value of that output might be significantly lower. She has unknowingly performed a bad trade due to the pending transaction she forgot about. It could have been possible that she may receive 105 of TokenB, however its her loss due to missing deadline while swapping tokens.


**Recommendation to fix**:
Add a deadline parameter to the swap function and ensure below condition.


```solidity

    modifier ensureDeadline(uint deadline) {
        require(deadline >= block.timestamp, 'Transaction expired');
        _;
    }
```
