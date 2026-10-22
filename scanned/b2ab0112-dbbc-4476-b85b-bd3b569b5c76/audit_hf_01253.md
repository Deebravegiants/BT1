# [C] Fix review Finding: Incorrect Calculation of amount_to_burn in liquid_unstake

## Summary
Severity: Critical
Contest weight: 0.7362
Dataset id: 5765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the liquid_unstake function, the calculation of amount_to_burn is incorrect:
• amount represents the amount of gold to be unstaked.
• config.liquid_amount represents the total amount of gold in the pool.
• rewards_mint.supply represents the total minted supply of reward tokens.
The current formula incorrectly calculates amount_to_burn as:
```solidity
let amount_to_burn = (amount as u128)
.checked_mul(self.config.liquid_amount.into())
.ok_or(Overflow)?
.checked_div(self.rewards_mint.supply.into())
.ok_or(Overflow)?;
```
This leads to an incorrect token burn amount, affecting the protocol's balance and potentially causing loss of funds.

## Recommendation
Use the correct formula, which ensures amount_to_burn is proportional to the unstaked gold relative to the total gold in the protocol:
```solidity
let amount_to_burn = (amount as u128)
.checked_mul(self.rewards_mint.supply.into())
.ok_or(Overflow)?
.checked_div(self.config.liquid_amount.into())
.ok_or(Overflow)?;
```
