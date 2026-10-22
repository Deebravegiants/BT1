# [M] The protocol treasury losses due to receiving

## Summary
Severity: Medium
Contest weight: 0.5957
Dataset id: 22608
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol treasury faces potential value erosion due to accumulating BORROWER_LP_TOKEN_ID tokens, which can diminish in value over time. Furthermore, there's a restriction on redeeming these tokens when the capacity threshold isn't met, leading to potential asset lock-up. The treasury receives withdrawal fees in both LENDER_LP_TOKEN_ID and BORROWER_LP_TOKEN_ID tokens. However, due to the mechanism of interest compounding for lenders, the value of BORROWER_LP_TOKEN_ID tokens decreases over time as the borrower's net asset value diminishes. This decrease is a direct consequence of the lender balance increment through _compoundInterest(), which effectively reduces the borrower's share in the net asset value. The process exacerbates when considering the protocol's inability to redeem BORROWER_LP_TOKEN_ID tokens under certain conditions, such as when the LiquidityWarehouse is inactive or the requested withdrawal amount exceeds the capacityThreshold. This creates a scenario where the treasury could be holding depreciating assets with limited options for conversion back to liquid assets. Asset losses, temporary assets blocking.
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
```solidity
// L372
function getBorrowerNetAssetValue() public view returns (uint256) {
    return getNetAssetValue() - getLenderNetAssetValue();
}

function getLenderBalance() public view returns (uint256) {
    uint256 lenderBalance = s_assetData.lenderBalance;
    if (!s_isActive) return lenderBalance;
    uint256 compoundedInterest = MathUtils.calculateCompoundedInterest(
        uint256(s_terms.interestRate).wadToRay(),
        s_assetData.interestLastUpdatedAt, block.timestamp
    ).rayToWad();
    return lenderBalance.wadMul(compoundedInterest);
}
```
```solidity
// L229
function withdrawBorrower(uint256 shareAmount, address[] calldata withdrawTargets, bytes calldata data)
    external
    nonReentrant
{
    if (s_isActive && !_isCapacityThresholdFulfilled()) {
        revert CapacityThresholdBreached();
    }
    // L223
    uint256 withdrawalFee = uint256(s_terms.withdrawalFee);
    uint256 feeAmount = withdrawalFee.wadMul(withdrawableAmount);
    uint256 withdrawableAmountAfterFee = withdrawableAmount - feeAmount;
    _safeTransferFrom(
        msg.sender, s_terms.feeRecipient, BORROWER_LP_TOKEN_ID,
        withdrawalFee.wadMul(shareAmount), bytes("")
    );
}
```

## Recommendation
The protocol should consider structuring withdrawal fees from borrowers in the underlying asset tokens instead of BORROWER_LP_TOKEN_ID tokens. This adjustment would safeguard the treasury from the negative impact of depreciating token values and restrictive withdrawal conditions.
