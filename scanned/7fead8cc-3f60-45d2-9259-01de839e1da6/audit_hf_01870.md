# [M] M-21 Unreachable Code in updateThreshold Function

## Summary
Severity: Medium
Contest weight: 0.1005
Dataset id: 10402
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue is identified within the multiUseSignCondition.sol#L78-L85 function of the MultiUseSignCondition contract. The function contains a check to ensure that only an owner of the BORG_SAFE can update the threshold. However, this check will always fail because the onlyOwner modifier requires msg.sender to be the BORG_SAFE contract itself, which conflicts with the check inside the function that requires msg.sender to be an owner of BORGSAFE. Since the BORGSAFE contract cannot be an owner of itself, any call to this function will always revert.

## Recommendation
We recommend removing the check if (!ISafe(BORG_SAFE).isOwner(msg.sender)) within the updateThreshold function. Since the onlyOwner modifier already restricts access to the BORG_SAFE contract, additional checks inside the function are redundant and cause the function to always revert.
