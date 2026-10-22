# [H] Several Business Logic Errors in PositionStorage::tradeOut()

## Summary
Severity: High
Contest weight: 0.7852
Dataset id: 12979
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the SatoshiSwap protocol has a SatoshiSwap Margin Trading Module which provides the operations of opening a LONG or SHORT position in accordance with the settings for Public trading with the SatoshiSwap Exchange Module. To facilitate it, the PositionStorage contract also provides another helper routine, i.e., tradeOut(), that is designed to convert the quoteToken to demand baseToken when a short position is closed. To elaborate, we show below the related code snippet.
```solidity
function tradeOut(PositionLibrary.Trade memory _trade) internal returns (uint256 swapAmount) {
    //The detailed implementation removed per the request from the team
}
```
While analyzing this routine, we notice there are several logic errors. The first one is when this routine calculates how much _trade.baseToken is needed to do the exchange, _trade.input.add(_trade.input.mul(_trade.slippage)). This will route extra _trade.input.mul(_trade.slippage) amount of _trade.baseToken into the DEX. The second one is the requirement of _trade.input <= reserve0. This is problematic because reserve0 is mapped to the total balance of token0 from SatoshiPair, which may not be _trade.baseToken! This will cause the checking of this requirement invalid and further introduce a denial-of-service error when performing tradeOut(). Note the same issue is also applicable on the requirement of input[0] <= reserve1. The third one is the swapAmount which is calculated from balanceAfter.sub(balanceBefore). Semantically, swapAmount should be used to represent the swapped amount of _trade.quoteToken (_position.baseToken). However, as the return value of tradeOut(), swapAmount is also used as the profitAmount in _closePositionShort(), which is a logic error. To keep consistency with the implementation in MarginPool::closePosition(), we need to subtract the actual balanceAfter.sub(balanceBefore) from _position.swapAmount to yield the proﬁt.
```solidity
function closePosition(uint256 _positionId, uint256 _slippage) external nonReentrant emergencyShutdown {
    //The detailed implementation removed per the request from the team
}
```

## Recommendation
Correct the logic error mentioned above accordingly.
