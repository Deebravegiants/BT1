# [M] InternalizeDonations will never work for

## Summary
Severity: Medium
Contest weight: 0.4063
Dataset id: 2637
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If any tokens are donated to the InfraredCollateralVault, owner can call internalizeDonations and create a linear vesting for the newly donated funds. The exact donated amount is calculated in the following line:
```solidity
uint donatedAmount = IERC20(token).balanceOf(address(this)) - getBalanceOfWithFutureEmissions(token);
```
require(donatedAmount >= amount, "CollVault: insufficient balance"); It subtracts the virtual balance from the actual token balance and treats it as donation. The problem when this asset is the main asset, is that usually the token balance would be 0, while the virtual accounting would be high. This is because all deposited assets get staked directly in the Infrared Vault. This would make the line above revert due to underflow and if any funds are sent as donation, they'd simply remain stuck. Same issue exists also in receiveDonations Logic issue Loss of funds/ Stuck funds, Broken functionality Affected Code edCollateralVault.sol#L237

## Recommendation
Usually if there's any asset balance within the contract, it should be treated as donation
