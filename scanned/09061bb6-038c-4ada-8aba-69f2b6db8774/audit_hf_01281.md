# [M] Inconsistency in minimum value out for native deposits via receive function

## Summary
Severity: Medium
Contest weight: 0.3928
Dataset id: 6034
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the receive() function calls the deposit() function with a hardcoded minimum value out of 0 for native deposits. This design could potentially lead to situations where users making native deposits do not have the opportunity to specify a minimum mint amount, differing from the ERC20 deposit flow where a minimumMint value is required. This inconsistency might result in unexpected outcomes for users, especially in volatile market conditions where the value of shares could change significantly before the transaction is processed.  
```solidity
/**
* @dev Depositing this way means users can not set a min value out.
*/
receive() external payable {
    deposit(ERC20(NATIVE), msg.value, 0);
}
```

## Recommendation
To ensure consistency and protect users from market volatility, it is recommended to delete receive() function.
