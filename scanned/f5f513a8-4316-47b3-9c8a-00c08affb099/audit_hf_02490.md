# [C] Flashloan-Based Oracle Price Manipulation

## Summary
Severity: Critical
Contest weight: 0.6297
Dataset id: 13324
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Velvet Capital protocol has a PriceOracle contract to facilitate the token price discovery. Our analysis shows the current approach to compute the on-chain token price can be manipulated.
```solidity
function getTokenPrice(address token_address, address token1_address)
    external
    view
    override
    returns (uint256 price)
{
    uint256 token_decimals = IERC20Metadata(token_address).decimals();
    uint256 min_amountIn = 1 * 10**token_decimals;
    if (token_address == token1_address) {
        price = min_amountIn;
    } else {
        (uint256 reserve0, uint256 reserve1) = getReserves(token_address, token1_address);
        price = uniswapV2Router.getAmountOut(
            min_amountIn,
            reserve0,
            reserve1
        );
    }
}
```
To elaborate, we show above the related getTokenPrice() function. It comes to our attention that the conversion is routed to UniswapV2-based DEXs and the related spot reserves are used to compute the price! Therefore, they are vulnerable to possible front-running attacks, resulting in possible loss for the token conversion. Note that this is a common issue plaguing current AMM-based DEX solutions. Specfically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop an effective mitigation (e.g., slippage control) to the above front-running attack to better protect the interests of protocol users.
