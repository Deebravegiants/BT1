# [M] Incorrect setFee()/removeFee() Logic in RadiantStaking

## Summary
Severity: Medium
Contest weight: 0.4593
Dataset id: 12875
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The RadiantStaking contract is the main contract that enables users zap into DLP positions to get boosted yield and vote. The contract has two arrays radiantFeeInfos and rTokenFeeInfos to manage the reward fee and recipients. While examining the current logic to manage these two arrays, we notice the implementation does not follow the intended logic. To elaborate, we show below the implementation of two related routines setFee() and removeFee(). As the names indicate, the first routine is used to update the fee configuration for a given entry while the second one removes a specific fee entry. It comes to our attention that the first routine needs to be revised to update the totalRDNTFee value if the input _isRDNTFee is true. Otherwise, it should be the totalRTokenFee value. Also the given fee entry should be validated against feeInfo.length if _isRDNTFee is false.
```solidity
function setFee(
    uint256 _index,
    uint256 _value,
    address _to,
    bool _isRDNTFee,
    bool _isAddress,
    bool _isActive
) external onlyOwner {
    if (_value > DENOMINATOR) revert InvalidFee();
    if (_index >= radiantFeeInfos.length) revert InvalidIndex();
    Fees[] storage feeInfo;
    if (_isRDNTFee) feeInfo = radiantFeeInfos;
    else feeInfo = rTokenFeeInfos;
    Fees storage fee = feeInfo[_index];
    fee.to = _to;
    fee.isAddress = _isAddress;
    fee.isActive = _isActive;
    totalRDNTFee = totalRDNTFee - fee.value + _value;
    fee.value = _value;
    emit SetFee(_to, _value);
}

/// @dev remove some fee
/// @param _index the index of the fee in the fee list
/// @param _isRDNTFee true if the fee is for RDNT, false if it is for rToken
function removeFee(uint256 _index, bool _isRDNTFee) external onlyOwner {
    if (_index >= radiantFeeInfos.length) revert InvalidIndex();
    Fees[] storage feeInfos;
    if (_isRDNTFee) feeInfos = radiantFeeInfos;
    else feeInfos = rTokenFeeInfos;
    Fees memory feeToRemove = feeInfos[_index];
    if (feeToRemove.isActive) revert StillActiveFee();
    for (uint256 i = _index; i < radiantFeeInfos.length - 1; i++) {
        radiantFeeInfos[i] = radiantFeeInfos[i + 1];
    }
    radiantFeeInfos.pop();
    emit RemoveFee(feeToRemove.value, feeToRemove.to, feeToRemove.isAddress);
}
```
Similarly, in the second removeFee() routine, the given fee entry should be validated against feeInfo.length if _isRDNTFee is false. And the fee removal should be applied to the feeInfos array, instead of the radiantFeeInfos.

## Recommendation
Revisit the above two routines to properly update the fee entry.
