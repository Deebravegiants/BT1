# [H] Business Logic Error in PositionStorage::tradeIn()

## Summary
Severity: High
Contest weight: 0.6173
Dataset id: 12955
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SatoshiSwap protocol has a SatoshiSwap Margin Trading Module which provides the operations of opening a LONG or SHORT position in accordance with the settings for trading with the SatoshiSwap Exchange Module. To facilitate it, the PositionStorage contract provides a helper routine, i.e., tradeIn(), that is designed to convert user assets into the demanding tokens. To elaborate, we show below the related code snippet.
```solidity
function tradeIn(PositionLibrary.Trade memory _trade) internal returns (uint256 swapAmount) {
    uint256 balanceBefore = IERC20Upgradeable(_trade.quoteToken).balanceOf(address(this));
    // execute trade
    ISatoshiRouter(exchangeRouter()).swapExactTokensForTokensSupportingFeeOnTransferTokens(
        _trade.input,
        0,
        _trade.path,
        address(this),
        block.timestamp.add(delay)
    );
    uint256 balanceAfter = IERC20Upgradeable(_trade.quoteToken).balanceOf(address(this));
    // calculate out amount
    swapAmount = balanceAfter.sub(balanceBefore);
    require(swapAmount > 0, "Margin Pool: Swap failed");
    if (swapAmount < _trade.swapAmount) {
        IERC20Upgradeable(_trade.baseToken).safeTransferFrom(_trade.sender, address(this), _trade.swapAmount - swapAmount);
    }
}
```
We notice this routine swaps baseToken to quoteToken and checks if the resulting swapAmount is smaller than the needed _trade.swapAmount. If yes, the routine will transfer the _trade.swapAmount - swapAmount amount of baseToken, from _trade.sender to PositionStorage. Since both of the _trade.swapAmount and swapAmount are amounts of quoteToken, it is a logic error to transfer the _trade.swapAmount - swapAmount amount of baseToken from _trade.sender.

## Recommendation
Correct the above logic error accordingly.
