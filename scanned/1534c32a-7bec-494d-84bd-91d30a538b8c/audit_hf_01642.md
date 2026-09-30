# [C] Lack of slippage protection during ETH to Hotkey swap in pool finalization

## Summary
Severity: Critical
Contest weight: 0.6180
Dataset id: 8793
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upon reaching a certain market cap of the newly created token, finalization phase is triggered, during which a Uniswap V3 pool is created, and liquidity is deposited into it. During finalization, the available ETH is swapped into Hotkey tokens because the pair of the newly created pool is Token/Hotkey. The problem with the implementation of this swap is that the parameter amountOutMinimum: 0 is used, which means there is no slippage protection.
```solidity
ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
    tokenIn: weth,
    tokenOut: hotKey,
    fee: 10000,
    recipient: address(this),
    amountIn: wethBalance, // All ETH balance
    amountOutMinimum: 0,
    sqrtPriceLimitX96: 0
});
```
This could lead to an unfavorable exchange rate and loss of funds. A malicious user could exploit this by executing a sandwich attack and extracting value from the process. An example scenario is as follows:  
1) The malicious user can trigger the finalization process in two ways: by executing buyToken() with enough ETH to exceed the finalMarketCap, or by frontrunning a transaction that would trigger finalization. They then perform a swap, purchasing Hotkey tokens for a certain amount of ETH from the Hotkey/ETH Uniswap pool.  
2) The HotCurves contract swaps its ETH for Hotkey, which increases the price of Hotkey measured in ETH. Due to the purchase in step 1), this happens at a very unfavorable rate for the protocol.  
3) The malicious user swaps the Hotkey tokens purchased in step 1 back to ETH, receiving more ETH than they initially spent.

## Recommendation
The solution is to implement slippage protection using the amountOutMinimum parameter. This minimum output amount should be based on a TWAP price (e.g., 5-minute interval) retrieved from the Uniswap pool with a reasonable tolerance to protect against price manipulation and ensure a fair exchange rate.
