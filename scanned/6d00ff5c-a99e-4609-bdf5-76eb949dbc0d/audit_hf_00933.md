# [M] M-4 Admin can drain all rewards from all incentives

## Summary
Severity: Medium
Contest weight: 0.0425
Dataset id: 2850
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an admin‑controlled backdoor that allows the contract owner to withdraw the entire pool of reward tokens from every farming incentive. The root cause lies in the decreaseRewardsAmount function, which unconditionally transfers the specified reward amount to the admin address without validating that the caller is the incentive’s registered reward source or that the withdrawal respects any accounting limits. Because the function is exposed to the admin and lacks granular access control, the admin can invoke it at any time and repeatedly request the full remaining balance, effectively draining all rewards. Exploitation is straightforward: the admin calls decreaseRewardsAmount with the total reward amount for a given incentive, the contract sends those tokens to the admin, and the same can be repeated for each incentive, leaving no rewards for participants. The impact is a loss of expected earnings for users who have staked tokens, resulting in balances that appear empty or unchanged despite active farming, and a breach of trust in the incentive mechanism. This condition occurs whenever the admin decides to execute the function, which can be after deployment and at any later block. All participants in the farming protocol—liquidity providers, token holders, and any downstream applications—are affected because the promised reward distribution is nullified. The issue was identified during a manual security audit that examined the reward‑adjustment logic and noticed the direct transfer to the admin address. It can be hard to notice because the function may be documented as a legitimate administrative tool for adjusting rewards, and the transfer to the admin is not flagged as suspicious by standard static analysis. To remediate, the reward‑refund logic should be redesigned so that only the address registered for a specific incentive can receive refunds, and any reduction of rewards must be accounted for against the incentive’s own balance rather than sent to the admin. Implementing stricter access controls, multi‑signature governance, or removing the direct admin transfer altogether will close the backdoor and restore confidence in the reward accounting system.

## Recommendation
We recommend changing the logic of rewards refunds. An incentive for specific farming should be controlled by a registered address for this incentive.
