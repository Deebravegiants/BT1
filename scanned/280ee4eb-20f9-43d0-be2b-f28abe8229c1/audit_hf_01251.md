# [C] Incorrect init Constraint in toggle_liquid Causes Fund Locking and DoS

## Summary
Severity: Critical
Contest weight: 0.5700
Dataset id: 5761
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The toggle_liquid function is completely frozen because it uses the init constraint with the config account. Since the init constraint is already used in the initialize_config function, any attempt to call toggle_liquid will always revert. This results in two critical issues affecting the protocol’s functionality:
1. Fund Locking: If toggle_liquid is responsible for initialization, the bump seeds used for signing the transfer CPI will not be stored hence the signing will not work permanently. This will lead to a complete lock of funds for all tokens staked by users.
2. Denial of Service: If initialize_config is used for initialization, the liquid_staking program will be permanently disabled because the liquid field in the config account will always remain false. As a result, the liquid_stake function will always revert, preventing staking operations.

## Recommendation
Modify the config account in the toggle_liquid function to avoid reinitialization. The corrected implementation is as follows:
```solidity
**[account(:** mut,
seeds = [b"config".as_ref()],
bump = config.bump,
)]
```
