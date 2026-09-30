# [M] Fix review Finding: Admin Can Reset Critical Configuration by Reinitializing the Contract

## Summary
Severity: Medium
Contest weight: 0.5597
Dataset id: 5759
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In liquid_staking/src/contexts/init.rs, there is a vulnerability in the Initialize context and its initialize_config() function. The root cause is that the config account is created with init_if_needed instead of init, allowing the admin to call the initialization function multiple times. The initialization code creates a config account as follows:
```solidity
**account(:** init_if_needed,
payer = admin,
seeds = [CONFIG_SEED.as_ref()],
bump,
space = 8 + State::INIT_SPACE,
)
```
When initialize_config() is called, it sets the State structure with crucial values including bump, liquid, liquid_amount, and monthly_rewards. Because the function can be called multiple times due to the init_if_needed constraint, the admin can reset these properties to arbitrary values at any time. This is particularly dangerous because:
1. The monthly_rewards parameter can be changed to manipulate rewards.
2. The liquid flag and liquid_amount fields can be reset, causing funds to be locked.

## Recommendation
Change the constraint from init_if_needed to init to ensure the initialization can only happen once:
```solidity
**[account(:**
-
init_if_needed,
+
init,
payer = admin,
seeds = [CONFIG_SEED.as_ref()],
bump,
space = 8 + State::INIT_SPACE,
)]
```
