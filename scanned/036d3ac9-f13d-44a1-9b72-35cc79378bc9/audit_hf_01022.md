# [H] Users can refund before the sale has ended

## Summary
Severity: High
Contest weight: 0.8681
Dataset id: 3765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function claimRefund allows a user to claim a refund if the drop was not successful. The problem occurs because of incorrect inequality checks that allow a user to refund while purchases of said drop are still possible.
```solidity
function claimRefund(uint256 dropId, uint256[] calldata wrappedTokenIds) external {
    Drop memory drop = _drops[dropId];
    uint256 dropStartTokenId = dropToStartTokenId[dropId];
    if (drop.tokensSold >= drop.minSellOutTokens) {
        _revert(RefundNotAvailable.selector);
    }
    if (block.timestamp < drop.saleEndTime) {
        _revert(RefundNotAvailable.selector);
    }
```
Let's focus on the last if statement, if the timestamp is equal to the end time then the logic execution continues. This is an error because at the time block.timestamp == drop.saleEndTime the drop is still live and allows users to make purchases of the drop. We can observe this from the snippet below from the purchaseDrop function
```solidity
if (block.timestamp > drop.saleEndTime)
    _revert(SaleEnded.selector);
```
as we can see there is a time period where block.timestamp == drop.saleEndTime that allows both refunding and purchasing of the drop.

## Recommendation
```solidity
if (block.timestamp <= drop.saleEndTime) {
    _revert(RefundNotAvailable.selector);
}
```
