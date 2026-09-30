# [M] Fee can be set to 100%

## Summary
Severity: Medium
Contest weight: 0.0775
Dataset id: 16239
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Vault docs we can see the following: The vault fee is 8% of the rewards earned by the vault. Now let's look at the code: function setFee(uint32 newFee) external onlyOwner { if (newFee > _FEE_BASIS) { revert InvalidAmount(newFee); _FEE_BASIS is equal to 100% meaning that the newFee can be set to be up to 100%. Plus there is not a lower constraint, meaning the fee can be set to 0% as well.

## Recommendation
Either mention in the docs that the fee can be changed but it is 8% for now or set a reasonable upper and lower constraint for fee. For example, 15% as an upper limit and 2% as a lower limit, if the newFee is set out of these boundaries - revert.
