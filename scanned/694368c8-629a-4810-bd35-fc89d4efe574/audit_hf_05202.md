# [H] Direct amount assignment in SherpaUSD::ownerMint/ownerBurn can break accounting for totalStaked and accountingSupply

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23329
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: Functions SherpaUSD::ownerMint and ownerBurn directly assign the amount parameter to mappings approvedTotalStakedAdjustment and approvedAccountingAdjustment. This will however not work correctly if more tokens are minted or burned to/from the vault before the approvals are consumed.

For example:
• Operator mints 100 SherpaUSD to SherpaVault.  
• This tracks approvedTotalStakedAdjustment and approvedAccountingAdjustment as 100 SherpaUSD each  
• Operator performs another mint of 200 tokens before the previous approvals are consumed.  
• Now the issue is that approvedTotalStakedAdjustment and approvedAccountingAdjustment will be overwrit‑ten to store 200 SherpaUSD each instead of 300 SherpaUSD.  
• This is clearly incorrect and breaks accounting since old approvals were not consumed yet by the vault.

```solidity
function ownerMint(address to, uint256 amount) external onlyOperator {
    _mint(to, amount);
    // Approve vault to adjust by this amount
    approvedTotalStakedAdjustment[to] = amount;
    approvedAccountingAdjustment[to] = amount;
    emit PermissionedMint(to, amount);
    emit RebalanceApprovalSet(to, amount, amount);
}

/**
 * @notice Operator-level burn for manual rebalancing across chains
 * @param from Address to burn from
 * @param amount Amount to burn
 * @dev Sets approval for vault to adjust totalStaked and accountingSupply
 */
function ownerBurn(address from, uint256 amount) external onlyOperator {
    _burn(from, amount);
    // Approve vault to adjust by this amount
    approvedTotalStakedAdjustment[from] = amount;
    approvedAccountingAdjustment[from] = amount;
    emit PermissionedBurn(from, amount);
    emit RebalanceApprovalSet(from, amount, amount);
}
```

## Recommendation
Recommended Mitigation: Consider replacing direct amount assignments with the += and -= operators in ownerMint and ownerBurn respectively.
