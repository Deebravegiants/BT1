# [M] VLT-5 | Vault is not ERC4626 Compliant

## Summary
Severity: Medium
Contest weight: 0.1407
Dataset id: 20592
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Vault does not respect several requirements needed to be ERC4626 compliant, although the internal documentation states that it is compliant: /// @notice While this contract is fully ERC4626 compliant, it also has additional functionality The non-compliance issues are: withdraw and redeem always revert; does not respect any of EIP requirements if the flagshipToken is removed from the vault via removeLst then deposit reverts. At this point maxDeposit must return 0, but it does not. ○ MUST factor in both global and user-specific limits, like if deposits are entirely disabled (even temporarily) it MUST return 0. convertToShares also reverts when this is not allowed ○ MUST NOT revert unless due to integer overflow caused by an unreasonably large input. previewRedeem and previewWithdraw do not take into consideration vault fees ○ MUST be inclusive of withdrawal fees. Integrators should be aware of the existence of withdrawal fees.

## Recommendation
Modify the above issues to match the standard. Also do not allow the flagship asset to be removed from the allowed LST list.
