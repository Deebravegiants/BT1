# [M] Incorrect withdraw Logic In HegicOperationalTreasury

## Summary
Severity: Medium
Contest weight: 0.4228
Dataset id: 12217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HegicOperationalTreasury contract provides an external function (i.e., withdraw()) for privileged DEFAULT_ADMIN_ROLE to withdraw deposited tokens from the contract. Our analysis with this routine shows its current implementation is not correct. To elaborate, we show below the code snippet of the withdraw()/_withdraw() functions. Its logic is rather straightforward in deducting the withdrawn amount from the internal record and transfer the tokens to the withdrawer. However, the imposed requirement is not correct. Specifically, the requirement require(amount + totalLocked <= totalBalance) should be revised as require(amount + totalLocked + lockedPremium <= totalBalance + stakeandcoverPool.availableBalance()), so that the contract keeps a guaranteed amount of tokens for the Hegic protocol users.
```solidity
* @notice
Used for withdrawing deposited tokens from the contract
* @param to The recipient address
* @param amount The amount to withdraw
function withdraw(address to, uint256 amount)
external onlyRole(DEFAULT_ADMIN_ROLE)
{
    _withdraw(to, amount);
}

function _withdraw(address to, uint256 amount) private {
    require(amount + totalLocked <= totalBalance);
    totalBalance -= amount;
    token.transfer(to, amount);
}
```

## Recommendation
Revise the require statement to make sure the contract keeps a guaranteed amount of tokens for the Hegic protocol users after the withdraw operation.
