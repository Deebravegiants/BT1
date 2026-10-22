# [C] C-02 | Current Constants.GMX_REWARD_ROUTER Was Disabled By GMX Team

## Summary
Severity: Critical
Contest weight: 0.2307
Dataset id: 2024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current reward router GMX_REWARD_ROUTER =
0x159854e14A862Df9E39E1D128b8e5F70B4A3cE9B; present in the Constants.sol file has been
deprecated by GMX in a recent [transaction.](https://arbiscan.io/tx/0xcb8f8ada8d9f4afb9e49f25f55d06fd46f40ef9453c1a9e7700f10459cb23174)
A [new reward router](https://arbiscan.io/address/0x5E4766F932ce00aA4a1A82d3Da85adf15C5694A1) is now being used. Consequently, any operation on the old
reward router will revert, affecting the functionality of contracts that rely on it. The ExitVault contract
uses the deprecated reward router address for various operations, such as staking and unstaking
GMX tokens.
This reliance on the outdated address will cause these operations to fail. Do also note that the [new
reward router](https://arbiscan.io/address/0x5E4766F932ce00aA4a1A82d3Da85adf15C5694A1)
interacts with a new RewardTracker (ExtendedGmxTracker) which includes GMX tokens as reward.

## Recommendation
Consider updating the Constants.GMX_REWARD_ROUTER to the new reward router address. Ensure
that the protocol is ready to also support the GMX rewards now given by the ExtendedGmxTracker.
