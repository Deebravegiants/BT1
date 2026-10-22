# [M] Possible Sandwich/MEV Attacks For Reduced Conversion

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 12956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the SatoshiSwap protocol has a PositionStorage contract which is used to store the positions and related operations with them. Inside the PositionStorage contract, there is a helper routine, i.e., tradeIn(), that is designed to convert user assets into the demanding tokens. To elaborate, we show below the related code snippet.
```solidity
function tradeIn(PositionLibrary.Trade memory _trade) internal returns (uint256 swapAmount) {
    (uint256 reserve0, uint256 reserve1, ) = pair.getReserves();
    uint256 output = 0;
    // calculate estimate amount out using constant product formula
    if (tokenPair1 == _trade.baseToken) {
        output = SatoshiLibrary.getAmountOut(_trade.input, reserve0, reserve1);
    } else {
        output = SatoshiLibrary.getAmountOut(_trade.input, reserve1, reserve0);
    }
    require(output > 0, "Margin Pool: Satoshi Pool doesnt have reserve");
    // calculate amount with slippage
    uint256 outputWithSlippage = (output.sub(((output.mul(_trade.slippage)).div(denominator()))));
    // execute trade
    ISatoshiRouter(exchangeRouter()).swapExactTokensForTokensSupportingFeeOnTransferTokens(
        _trade.input,
        outputWithSlippage,
        _trade.path,
        address(this),
        block.timestamp.add(delay)
    );
}
```
We notice the token swap is routed to a router SatoshiRouter. And the actual swap operation swapExactTokensForTokensSupportingFeeOnTransferTokens() specify an invalid restriction on slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller converted amount. Another routine tradeOut() shares the same issue. Note that this is a common issue plaguing current AMM-based DEX solutions. Speciﬁcally, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user or the virtual account in our case because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search eﬀorts for an eﬀective defense.

## Recommendation
Develop an effective mitigation to the above sandwich attack to better protect the interests of protocol users.
