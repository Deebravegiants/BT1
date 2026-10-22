# [M] The current beneficiary may be allowed to call the proposeBeneficiary() function

## Summary
Severity: Medium
Contest weight: 0.4074
Dataset id: 4287
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The NatSpec of the proposeBeneficiary() function specifies that the function is restricted
to only the contract owner. In IVestingWallet.sol#L152-L156:
```solidity
/**
* @notice Proposes a new beneficiary. This can only be called by the owner of the contract.
* @param _newBeneficiary The new beneficiary.
*/
function proposeBeneficiary(address _newBeneficiary) external;
```
Technically, the owner of the contract is the beneficiary. However, in the actual implementation, the
function is guarded by requiresAuth, so the caller does not necessarily have to be the owner.
Moreover, the owner (i.e., beneficiary) should not have the permission to call the proposeBeneficiary()
function. Otherwise, it could change the beneficiary to another address at any time without delay, which
goes against the purpose of the two-step design of the beneficiary change and potentially bypasses the
Governor.

## Recommendation
For the code, consider adding a check to the proposeBeneficiary() function to ensure the caller is not the current beneficiary explicitly. For the NatSpec, consider changing the comments to "This can only be called by an authorized caller except the current beneficiary." A similar change also applies to IVestingWallet.sol#L32.
