# [C] Incorrect Reward token calculation enables pool drain via arbitrage

## Summary
Severity: Critical
Contest weight: 0.7360
Dataset id: 5770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquid_stake() function contains a critical mathematical error in calculating the amount of reward tokens to mint to stakers when the rewards mint supply is non-zero. The current implementation calculates the reward amount as:
```solidity
amount * self.config.liquid_amount / self.rewards_mint.supply
```
The root cause is in the reward calculation logic where the numerator and denominator are swapped. This creates a situation where malicious users can:
1. Perform liquid_stake() to receive an inflated amount of reward tokens.
2. Use liquid_unstake() to withdraw more underlying tokens than initially deposited.
3. Repeat until the pool is drained.

## Recommendation
The reward token calculation should be corrected to maintain proper proportions between deposits and rewards. Update the calculation to:
```solidity
- amount * self.config.liquid_amount / self.rewards_mint.supply
+ amount * self.rewards_mint.supply / self.config.liquid_amount
```
