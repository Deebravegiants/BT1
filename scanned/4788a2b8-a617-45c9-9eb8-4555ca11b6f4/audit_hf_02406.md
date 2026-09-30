# [M] Inconsistent Fee Calculation Between MarginPool And PositionStorage

## Summary
Severity: Medium
Contest weight: 0.4245
Dataset id: 12957
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function closePosition(uint256 _positionId, uint256 _slippage) external nonReentrant emergencyShutdown {
    PositionLibrary.SuccessClosePosition memory output = IPoseitionStorage(positionStorage).closePosition(msg.sender, _positionId, _slippage);
    if (output.positionType == PositionLibrary.PositionType.LONG) {
        IERC20Upgradeable(token).safeTransferFrom(positionStorage, address(this), output.profitAmount);
        // insurance fee calculation
        uint256 profit = output.profitAmount.sub(output.ownedAmount);
        IERC20Upgradeable(token).safeTransfer(insurance, profit.mul(insuranceFee).div(denominator));
        IERC20Upgradeable(token).safeTransfer(
            msg.sender,
            output.profitAmount.sub(output.ownedAmount).sub(profit.mul(insuranceFee).div(denominator)).sub(output.poolInterestAmount)
        );
    }
}
```
While examining the logic of above function, we notice the fees are divided into two parts: insuranceFee and poolInterestAmount. However, the fee calculation in PositionStorage::_closePositionLong()/PositionStorage::_closePositionShort() only counts poolInterestAmount. The inconsistent fee calculation between MarginPool and PositionStorage may revert MarginPool::closePosition() when transferring the leftover tokens to msg.sender (line 245).

## Recommendation
Be consistent of fee calculation between MarginPool and PositionStorage.
