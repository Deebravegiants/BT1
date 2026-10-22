# [M] Trading Fee Discrepancy Between Kalmar And PancakeSwap

## Summary
Severity: Medium
Contest weight: 0.4568
Dataset id: 12352
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Kalmar protocol, a number of situations require the real-time swap of one token to another. For example, the StrategyAllBaseTokenOnly strategy takes only the base token and converts some portion of it to quote token so that their ratio matches the current swap price in the PancakeSwap pool. Note Public that in PancakeSwap, if you make a token swap or trade on the exchange, you will need to pay a 0.25% trading fee, which is broken down into two parts. The first part of 0.17% is returned to liquidity pools in the form of a fee reward for liquidity providers, the 0.03% is sent to the PancakeSwap Treasury, and the remaining 0.05% is used towards CAKE buyback and burn.
To elaborate, we show below the getAmountOut() routine inside the the UniswapV2Library. For comparison, we also show the getMktSellAmount() routine in MasterChefGoblin.
It is interesting to note that MasterChefGoblin has implicitly assumed the trading fee is 0.3%, instead of 0.25%.
The difference in the built-in trading fee may skew the optimal allocation of assets in the developed strategies (e.g., StrategyAddETHOnly and StrategyAddTwoSidesOptimal) and other contracts (e.g., MasterChefPoolRewardPairGoblin and MasterChefPoolRewardPairGoblin).
```solidity
// given an input amount of an asset and pair reserves, returns the maximum output amount of the other asset
function getAmountOut(
    uint256 amountIn,
    uint256 reserveIn,
    uint256 reserveOut
) internal pure returns (uint256 amountOut) {
    require(amountIn > 0, "UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT");
    require(reserveIn > 0 && reserveOut > 0, "UniswapV2Library: INSUFFICIENT_LIQUIDITY");
    uint256 amountInWithFee = amountIn.mul(997);
    uint256 numerator = amountInWithFee.mul(reserveOut);
    uint256 denominator = reserveIn.mul(1000).add(amountInWithFee);
    amountOut = numerator / denominator;
}
```
/// @dev Return maximum output given the input amount and the

## Recommendation
Make the built-in trading fee in Kalmar consistent with the actual trading fee in PancakeSwap.
Public
