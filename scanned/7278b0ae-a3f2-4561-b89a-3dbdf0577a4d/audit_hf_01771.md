# [M] Incorrect Share Accounting After Liquidation Leading to Ownership Dilution

## Summary
Severity: Medium
Contest weight: 0.4605
Dataset id: 9794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PerpetualVault contract incorrectly handles share accounting after a liquidation event when a new user deposits funds. Existing users’ shares remain unchanged despite the vault’s value dropping to zero, causing the new user’s ownership to be unfairly diluted. This results in an inaccurate distribution of vault ownership, violating the principle that a new depositor should own 100% of a vault with no prior value. 

In the _mint function, shares are calculated for a new depositor as follows: 

```solidity
uint256 _shares;
if (totalShares == 0) {
    _shares = depositInfo[depositId].amount * 1e8;
} else {
    uint256 totalAmountBefore = _totalAmount(prices) - amount;
    if (totalAmountBefore == 0) totalAmountBefore = 1;  // Avoid division by zero
    _shares = amount * totalShares / totalAmountBefore;
}
totalShares = totalShares + _shares;
```

After liquidation: 
totalAmountBefore (vault value before the deposit) is 0 because all value was lost. 
Existing users collectively own totalShares = A shares, unchanged from pre-liquidation. 
When a new user deposits amount: 
totalAmountBefore is set to 1. 
   _shares = amount * A / 1 = amount * A. 
   New totalShares = A + (amount * A) = A(1 + amount).
Ownership: 
Existing users: A / [A(1 + amount)]. 
   New user: (amount * A) / [A(1 + amount)] = amount / (1 + amount).
    For example, if amount = 1:
New user owns 50% (1 / (1 + 1) = 0.5). 
Existing users own 50%.
  This is incorrect because the new user, contributing all value post-liquidation, should own 100% of the vault—not have their ownership diluted by worthless pre-liquidation shares.
Ownership Dilution: The new depositor’s ownership is unfairly reduced (e.g., to 50% instead of 100%), despite contributing all post-liquidation value. 
Financial Inaccuracy: Existing users retain ownership over a vault they no longer have value in, potentially allowing them to claim future profits they don’t deserve. 
User Trust Erosion: This accounting flaw could deter new users who expect fair ownership proportional to their contribution, undermining the protocol’s integrity.

## Recommendation
Reset the share system when the vault’s value is zero post-liquidation to ensure the new depositor receives 100% ownership.
