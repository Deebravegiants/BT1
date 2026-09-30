# [H] Call selector mismatch will cause unstaking to revert

## Summary
Severity: High
Contest weight: 0.7186
Dataset id: 21933
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** In the Chainlink staking the `StakingPoolBase::unstake` call looks like this:
```solidity
function unstake(uint256 amount) external {
```
However in `Vault::withdraw` it is called like this:
```solidity
stakeController.unstake(_amount, false);
```

** Unstaking will not work until all vaults are updated.

## Recommendation
** Consider removing the `false` from `unstake`:
```diff
-       stakeController.unstake(_amount, false);
+       stakeController.unstake(_amount);
```
