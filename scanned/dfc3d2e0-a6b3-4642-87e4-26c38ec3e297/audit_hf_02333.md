# [M] Possible Sandwich/MEV For Reduced Returns

## Summary
Severity: Medium
Contest weight: 0.4605
Dataset id: 12682
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Pandora protocol has a unique incentivize mechanism that aims to engage trading and farming users. This is proposed to address the shortcomings of current DEXs and improve the user retention rates.
Within this process, there is a constant need of swapping one token to another.
While reviewing the related token-swapping logic, we notice the current implementation may be improved.
To elaborate, we show below the related Treasury::_swap() routine. As the name indicates, it has a rather straightforward logic in swapping the given amount of fromToken to toToken.
```solidity
function _swap(
    address fromToken,
    address toToken,
    uint256 amountIn
) internal returns (uint256 amountOut) {
    // Checks
    // X1 - X5: OK
    IUniswapV2Pair pair = IUniswapV2Pair(factory.getPair(fromToken, toToken));
    require(address(pair) != address(0), "Treasury: Cannot convert");
    // Interactions
    // X1 - X5: OK
    (uint256 reserve0, uint256 reserve1, ) = pair.getReserves();
    uint256 amountInWithFee = amountIn.mul(997);
    if (fromToken == pair.token0()) {
        amountOut = amountInWithFee.mul(reserve1) / reserve0.mul(1000).add(amountInWithFee);
        IERC20(fromToken).safeTransfer(address(pair), amountIn);
        pair.swap(0, amountOut, address(this), new bytes(0));
        // TODO: Add maximum slippage?
    } else {
        amountOut = amountInWithFee.mul(reserve0) / reserve1.mul(1000).add(amountInWithFee);
        IERC20(fromToken).safeTransfer(address(pair), amountIn);
        pair.swap(amountOut, 0, address(this), new bytes(0));
        // TODO: Add maximum slippage?
    }
}
```
We notice the current logic seems to validate the amount of returned amount. However, it is computed based on the instant DEX liquidity, which may be manipulated in frontrunning or MEV attacks. In other words, the current approach does not effectively specify the required restriction on possible slippage. As a result, it may result in a smaller amount of swapped amount.
Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop an effective mitigation to the above front-running situations to better protect the interests of trading/farming users.
