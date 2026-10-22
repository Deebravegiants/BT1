# [M] Interest will be compounded even when the

## Summary
Severity: Medium
Contest weight: 0.6930
Dataset id: 22609
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It compounds interest even during periods of inactivity, due to the absence of an interest update mechanism upon reactivation. The activate() function lacks an update to s_assetData.interestLastUpdatedAt. As a result, when the protocol transitions from an inactive to active state, interest accrued during the inactivity is incorrectly compounded. This scenario unfolds as follows:
1. The DebtCovenant contract deactivates the LiquidityWarehouse via deactivate(), triggering an update to interestLastUpdatedAt.
2. The protocol remains inactive for an extended period without user interactions.
3. The attacker (as a lender) donates tokens to fulfill the liquidation threshold.
4. DebtCovenant or attacker reactivates the protocol using activate(), but interestLastUpdatedAt remains unchanged.
5. Subsequent user interactions trigger interest compounding over the entire inactive period, leading to erroneous interest calculations and borrower losses.
This issue causes inaccurate interest compounding for the duration of the protocol's inactivity, potentially leading to financial discrepancies towards malicious lenders at the expense of borrowers.
```solidity
/// @inheritdoc ILiquidityWarehouse
function activate() external {
    if (!_isLiquidationThresholdFulfilled()) revert LiquidationThresholdBreached();
    _activate();
}
```
```solidity
/// @notice Updates the lender's balance with the interest owed
function _compoundInterest() internal {
    uint256 lenderBalanceBefore = uint256(s_assetData.lenderBalance);
    if (lenderBalanceBefore > 0 && s_isActive) {
        uint256 compoundedInterest = MathUtils.calculateCompoundedInterest(
            uint256(s_terms.interestRate).wadToRay(),
            s_assetData.interestLastUpdatedAt, block.timestamp
        ).rayToWad();
        s_assetData.lenderBalance =
            lenderBalanceBefore.wadMul(compoundedInterest).toUint216();
        uint256 earnedFeeAmount =
            uint256(s_terms.interestFee).wadMul(s_assetData.lenderBalance - lenderBalanceBefore);
        uint256 feeShareAmount =
            totalSupply(LENDER_LP_TOKEN_ID).wadMul(earnedFeeAmount).wadDiv(
                s_assetData.lenderBalance - earnedFeeAmount
            );
        _mint(s_terms.feeRecipient, LENDER_LP_TOKEN_ID, feeShareAmount, bytes(""));
    }
    s_assetData.interestLastUpdatedAt = block.timestamp.toUint40();
}
```

## Recommendation
To ensure interest calculations accurately reflect the protocol's active status, update the interestLastUpdatedAt timestamp upon activation:
```solidity
/// @inheritdoc ILiquidityWarehouse
function activate() external {
    if (!_isLiquidationThresholdFulfilled()) revert LiquidationThresholdBreached();
    _compoundInterest();
    _activate();
}
```
