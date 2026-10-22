# [H] Business Logic Error in PositionStorage::_openPosition()

## Summary
Severity: High
Contest weight: 0.7612
Dataset id: 12980
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the SatoshiSwap Margin Trading Module provides the operations of opening a LONG or SHORT position in accordance with the settings for trading with the SatoshiSwap Exchange Module. To facilitate it, the PositionStorage contract provides a helper routine, i.e., _openPosition(), that is designed to accept the user assets and add the leverage to open a position in quoteToken. To elaborate, we show below the related code snippet.
```solidity
function _openPosition() internal returns (uint256 ownedAmount, uint256 positionId) {
    //The detailed implementation removed per the request from the team
}
```
```solidity
function getAvailablePoolAmount(address _token) internal view returns (uint256) {
    return IGenericMarginPool(pool).getAvailablePoolAmount(_token);
}
```
```solidity
function openPosition() external nonReentrant emergencyShutdown {
    //The detailed implementation removed per the request from the team
}
```
We notice this routine checks the available amount for borrowing before executing the trade to open a position. However, the requirement of amountWithLeverage <= getAvailablePoolAmount(baseToken()) obtains the available amount of baseToken from MarginPool, which is a logic error. The reason is that baseTokens are already transferred into positionStorage before the calling of PositionStorage::_openPosition().

## Recommendation
Correct the logic error mentioned above accordingly.
