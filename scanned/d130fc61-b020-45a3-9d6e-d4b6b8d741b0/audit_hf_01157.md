# [M] Emergency withdraw fails to update total_supply, leading to protocol users receiving less rewards

## Summary
Severity: Medium
Reporter: 0xluk3, also found by 0xlookman, trachev, chupinexx, 0xpinkman, 0xb0k0, 0xAlexSR, IAM0TI, ZoA and undeﬁned
Contest weight: 0.2155
Dataset id: 4938
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The masterchef module relies on total_supply value which is part of entity pool_info.  
• On each deposit, total_supply is increased.  
• On each withdraw, total_supply is decreased.  
• On emergency_withdraw, however, it is not done.  
total_supply value is used by the update_pool function to calculate reward per share as a denominator,  
which in simple words mean that the larger the supply, the smaller the reward per share.  
Hence, with each emergency withdraw, the pool supply remains higher than it should, as if those users  
were still participating in total rewards distribution.  
This vulnerability can impact users organically, over time, as users emergency withdraw and the pool  
supply is not properly decreased, but also a malicious user can intentionally deposit and emergency withdraw a large amount of tokens which will inﬂate the total_supply causing all other users to receive less rewards.

Impact Explanation:  
High, because this may cause users to lose their rewards partially or entirely.

## Proof of Concept
• Scenario 1: Normal operation  
– Bob stakes 500 LP tokens, Alice stakes 500 LP tokens.  
* Total pool supply = 1000 LP tokens.  
* 1000 seconds pass with 1 reward token per second.  
– Reward Calculation:  
Total rewards = 1000 tokens  
acc_reward_per_share = 1000 rewards × 10^12 ÷ 1000 LP tokens = 10^12  
Bob's reward = 500 LP tokens × 10^12 ÷ 10^12 = 500 tokens  
Alice's reward = 500 LP tokens × 10^12 ÷ 10^12 = 500 tokens

## Recommendation
Update total_supply on emergency_withdraw as well by properly decreasing it by the withdrawn amount.
