# [C] CRT-2 Incorrect update of totalLiquidity

## Summary
Severity: Critical
Contest weight: 0.0758
Dataset id: 9269
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrectaccounting of the pool’s totalLiquidity variable in the staking rewards contract. The root cause lies in the update modifier that adjusts totalLiquidity unconditionally, even when the caller does not hold the required NFT that represents a stake. When a user executes the sequence deposit() → withdraw() → getReward(), the contract reduces the user’s balance but still increments totalLiquidity during the withdraw step, leaving the global liquidity figure higher than the actual amount of tokens locked. Because reward distribution is calculated as a function of totalLiquidity, the inflated figure skews the reward formula, allowing the attacker to receive a larger share of rewards than entitled or causing other participants to receive less. The exploit can be carried out by any participant who can deposit, immediately withdraw, and then claim rewards, thereby manipulating the accounting state before the reward calculation runs. The impact is a distortion of the reward economics: users may see unexpectedly high rewards, the protocol’s reward pool can be drained faster than intended, and overall trust in the staking mechanism is compromised. This condition occurs only when the contract’s update logic does not verify NFT ownership before adjusting totalLiquidity, which is triggered by the specific call order described. All stakers, the protocol’s token economics, and any downstream applications that rely on accurate reward numbers are affected. The issue was discovered during a manual security audit that examined state‑transition flows and identified that the totalLiquidity variable was not being guarded by the expected ownership check. Because totalLiquidity is an internal bookkeeping variable, the bug does not manifest as a direct UI error; instead, users notice that the reward amount they receive does not match the expected proportion, or that the reward pool depletes unusually fast, making the problem subtle and easy to miss. The recommended remediation is to revise the update modifier so that totalLiquidity is modified only when the contract actually holds the NFT representing a stake, or to recompute totalLiquidity after a withdraw before any reward calculation. In broader terms, this is a classic accounting‑state inconsistency bug where a global pool metric is updated without proper validation, leading to reward misallocation and potential fund loss.

## Recommendation
We recommend to change the logic of update modificator, so that totalLiquidity would update only if NFT is possessed to this contract.
2.2 MAJOR
