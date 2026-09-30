# [C] Missing mutable account constraint prevents state updates

## Summary
Severity: Critical
Contest weight: 0.5750
Dataset id: 5752
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The config account in liquid_stake(), liquid_unstake(), and reward() functions lacks the required mut constraint in the account validation, preventing critical state updates from being persisted. In Solana, accounts that need to be modified during instruction execution must be explicitly marked as mutable using the mut constraint. Without this constraint, any attempts to modify the account's data will not be persisted at runtime, even though the account is successfully loaded and the modification logic executes correctly.
The config account, which holds critical protocol state including liquid staking amounts and configuration parameters, is defined without the mut constraint in its account validation struct. As a result, while the code successfully executes state variable updates within this account (e.g., self.config.liquid_amount += amount in liquid_stake()), these changes are not persisted to the blockchain.

## Recommendation
Add the mut constraint to the config account validation in liquid_stake(), liquid_unstake(), and reward() functions. The fix should be applied as follows:
```solidity
**[account(:**
+
mut,
seeds = [b"config".as_ref()],
bump = config.bump,
)]
```
