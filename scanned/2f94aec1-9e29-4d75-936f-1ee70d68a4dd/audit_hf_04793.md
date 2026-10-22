# [M] Initial Liquidity provider can bypass the with-

## Summary
Severity: Medium
Contest weight: 0.1419
Dataset id: 22657
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The initial liquidity provider can bypass maximum withdrawal limit and withdraw all the liquidity that he has leading to a rug pull.
According to the protocol documentation, mandatory liquidity locks are liquidity each week. The check for this restriction is enforced within the `_beforeTokenTransfer` function as follows:
but this check isn't done if the number of withdrawals left for the lp is 1. so the initial liquidity provider can withdraw the whole amount of lp tokens that he has, bypassing the 25% limit.
Proof of Concept:
• Assume the initial liquidity provider holds 100 LP tokens of the pair tokenA/WETH, and the pool is in the AMM phase.
• Over the first three weeks, they burn 1 LP token each week.
• By the fourth week, they have 97 LP tokens remaining, and they withdraw all of them.
• This action effectively results in a rug pull, harming the users of the protocol.
a key invariant of the system gets breached by having the initial liquidity provider able to bypass the withdraw limit.

## Recommendation
No recommendation available
