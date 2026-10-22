# [C] Force Investment Risk in MarginPool::openPosition()

## Summary
Severity: Critical
Contest weight: 0.5950
Dataset id: 12982
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.7, the SatoshiSwap Margin Trading Module provides the operations of opening a LONG or SHORT position by a helper routine, openPosition(). This routine applies the user configured _quoteToken and _slippage arguments to open a position. To elaborate, we show below the related code snippet.
```solidity
function openPosition(
    address _quoteToken,
    PositionLibrary.PositionType _position,
    uint256 _amount,
    uint256 _leverage,
    uint256 _slippage
) external nonReentrant emergencyShutdown {
    _setBorrowedPoolAmount(_amount.mul(_leverage));
    PositionLibrary.SuccessOpenPosition memory output = IPositionStorage(positionStorage).openPosition(msg.sender, _quoteToken, _position, _amount, _leverage, _slippage);
}
```
We notice this routine transfers _amount.mul(_leverage) amount of baseToken to the PositionStorage contract and opens the leverage by swapping baseToken to quoteToken without valid slippage control. A bad actor could add a fake token and manipulate an imbalanced pool to force the MarginPool to open a position at an unfavorable exchange rate and do the reversed swap afterwards. Unfortunately, this force investment bug has been exploited in a recent incident (the veeFinance hack [1]) that prompts the need of _quoteToken validation in tokenList and careful _slippage management.

## Recommendation
Correct the above logic error accordingly.
