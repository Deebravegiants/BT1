# [M] _safeTransferToken() does not check the returned value of tokens

## Summary
Severity: Medium
Contest weight: 0.3980
Dataset id: 8035
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _safeTransferToken function in the FarmKeeper.sol uses the standard .transfer method to move ERC-20 tokens:  

```solidity
private {
    // In case if rounding error causes farm keeper to not have enough tokens.
    if (amount > balanace) {
        IERC20(token).transfer(to, balanace);
    } else {
        IERC20(token).transfer(to, amount);
    }
}
```

However, it does not check the return value of the .transfer function, which can lead to issues if the token contract does not behave as expected.  
In the ERC-20 standard, the transfer function returns a boolean value indicating success (true) or failure (false). If this return value is not checked, the function could assume the transfer succeeded when it may have failed, potentially leading to inconsistencies in the contract's state, unclaimed tokens, or loss of funds.

## Recommendation
Replace the current transfer() with safeTransfer() from OpenZeppelin.
