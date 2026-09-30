# [M] Large amount of points can STILL be minted

## Summary
Severity: Medium
Contest weight: 0.1487
Dataset id: 22677
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Out that the points could be minted without any cost, this issue still remains, and now the attacker can prevent other users from earning points. Following attack to mint a large number of points:
1. Deposit liquidity
2. After a short amount of time, withdraw it
3. Repeat the attack, minting a huge amount of points
This attack can still be executed to mint a large number of points at almost no cost. On the minted points. Even though this mitigation would reduce the profit of an attacker, it won't prevent the attacker from minting the maximum amount of points until the rate limit is reached.
Moreover, an attacker could use the rate limit to prevent other users from minting points. By constantly depositing and withdrawing liquidity, it would mint all points for himself until the rate limit is reached. Then, when other innocent users deposit liquidity or make trades, they won't receive any points.
The attacker can still mint a large amount of points, and prevent other users from receiving them.

## Recommendation
Reduce the amount of points earned when users withdraw liquidity or implement a withdrawal fee even if the LP is the last in the market.
