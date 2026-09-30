# [M] `loanLiquidation

## Summary
Severity: Medium
Contest weight: 0.5761
Dataset id: 21179
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function loanLiquidation(
    uint256 _loanId,
    uint256 _principalAmount,
    uint256 _apr,
    uint256,
    uint256 _protocolFee,
    uint256 _received,
    uint256 _startTime
) external override onlyAcceptedCallers {
    uint256 netApr = _netApr(_apr, _protocolFee);
    uint256 interestEarned = _principalAmount.getInterest(netApr, block.timestamp - _startTime);
    uint256 fees = IFeeManager(getFeeManager).processFees(_received, 0);
    getCollectedFees += fees;
    _loanTermination(msg.sender, _loanId, _principalAmount, netApr, interestEarned, _received - fees);
}
...
contract FeeManager is IFeeManager, TwoStepOwned {
...
    function processFees(uint256 _principal, uint256 _interest) external view returns (uint256) {
        /// @dev cached
        Fees memory __fees = _fees;
        return _principal.mulDivDown(__fees.managementFee, PRECISION)
            + _interest.mulDivDown(__fees.performanceFee, PRECISION);
    }
```

The above code takes all of `_received` as the principal and gives it to `IFeeManager` to calculate. But the amount received from the bidding is not always less than the principal, it may be more than the principal, and this part should be calculated as `interest`.

## Recommendation
```solidity
function loanLiquidation(
    uint256 _loanId,
    uint256 _principalAmount,
    uint256 _apr,
    uint256,
    uint256 _protocolFee,
    uint256 _received,
    uint256 _startTime
) external override onlyAcceptedCallers {
    uint256 netApr = _netApr(_apr, _protocolFee);
    uint256 interestEarned = _principalAmount.getInterest(netApr, block.timestamp - _startTime);
    uint256 fees;
    if (_received > _principalAmount) {
        fees = IFeeManager(getFeeManager).processFees(_principalAmount, _received - _principalAmount);
    } else {
        fees = IFeeManager(getFeeManager).processFees(_received, 0);
    }
    getCollectedFees += fees;
    _loanTermination(msg.sender, _loanId, _principalAmount, netApr, interestEarned, _received - fees);
}
```
