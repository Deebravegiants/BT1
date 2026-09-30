# [C] C-06 | User Voting Shares Can Be Burned By Others

## Summary
Severity: Critical
Contest weight: 0.2357
Dataset id: 22178
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The update function can be called by anyone to update another user's stake position. The issue lies in _update which burns a user's share balance if the CBR had decreased from the time when the user first staked. Consider this example: Alice stakes 10 pTKNs and received 10 voting shares. CBR is 1.0 CBR drops to 0.8 due to external factors Bob calls update on Alice's position. 2 shares are burned from her If Bob was unable to call update on Alice's position, she could choose to do nothing and preserve her shares, potentially waiting for CBR to recover before performing more staking actions. Furthermore, the CBR can be be drastically decreased with a flashloan from the pod, which would allow Bob to initially stake, flashloan to decrease CBR, and update Alice's position to burn all of her voting power. Consequently, Bob can have all the voting power and claim all the rewards at the expense of other stakers.

## Recommendation
Do not allow update to be called on another user's position and consider limiting direct balance checks. Also, do re-consider the design of the burn during _update as it will deter users from staking if their previous shares are burnt due to a change in CBR.
