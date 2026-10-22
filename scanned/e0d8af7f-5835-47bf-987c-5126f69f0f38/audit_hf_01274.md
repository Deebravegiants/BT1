# [M] Missing checks in the bulkDeposit and bulkWithdraw functions

## Summary
Severity: Medium
Contest weight: 0.4324
Dataset id: 6024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The bulkDeposit function in the contract is responsible for allowing users with the "onramp" role to deposit ERC20 tokens into the contract. However, this function lacks important checks that are present in other functions within the contract.  
Note : the bulkWithdraw is also missing isSupported check.  
Specifically, the bulkDeposit function does not have the following checks:  
• Pause Check: The function does not check if the contract is currently paused before allowing deposits. This means that deposits can be made even when the contract is in a paused state.  
• Token Support Check: The function does not verify if the provided depositAsset is a supported token by the contract. This could potentially allow deposits of unsupported tokens, leading to unexpected behavior or potential vulnerabilities.  
```solidity
/**
* @notice Allows on ramp role to deposit into this contract.
* @dev Does NOT support native deposits.
*/
function bulkDeposit(ERC20 depositAsset, uint256 depositAmount, uint256 minimumMint, address to)
external
requiresAuth
returns (uint256 shares)
{
    shares = _erc20Deposit(depositAsset, depositAmount, minimumMint, to);
    emit BulkDeposit(address(depositAsset), depositAmount);
}
```

## Recommendation
To address these issues, it is recommended to add the following checks to the bulkDeposit function:  
• Add a check to ensure that the contract is not paused before allowing deposits.  
• Add a check to verify that the provided depositAsset is a supported token by the contract.  
Se7en Seas:  
Fixed by adding the appropriate isSupported check to TellerWithMultiAssetSupport:bulkDeposit in commit 546ff962 and to bulkWithdraw in commit 59a18048. It is intentional for bulkDeposit to not check if the Teller is paused. Pausing is intended only to stop general public deposits, but permissioned deposits using the AtomicQueue should still be allowed.
