# [H] Adversary can steal all bribe rewards

## Summary
Severity: High
Chain: Smart contract
Component: Fenix-Finance
Published: 2024-02-27
Source: https://github.com/hats-finance/Fenix-Finance-0x83dbe5aa378f3ce160ed084daf85f621289fb92f/issues/2
Type: hats-finding

## Details
**Github username:** @deadrosesxyz
**Twitter username:** @deadrosesxyz
**Submission hash (on-chain):** 0x582d7050f2de893699c434f390798690c49a7e486b6c4f73d7cb4350370b2a7f
**Severity:** high

**Description:**
**Description**\
Adversary can steal all bribe rewards. I have previously reported the issue  to Retro, Thena and Chronos, so description is copied 

**Attack Scenario**\
So here's the attack path:

1. User mints lock for dust amounts. (let's say 1 wei) One for every added gauge within the project.
2. User votes 1 NFT to every different gauge.
3. User creates a lock for a relatively high amount of tokens. (let's say 1000e18)
4. A week passes. The user's balance in each gauge is now 0.
5. User votes with the high-value NFT for the first gauge. His balance there is now equivalent to this NFT's balance (1000e18)
6.User calls vote.reset for the low-value NFT at the same (first) gauge. His balance is then equal to the high-value NFT's - low-value NFT's (1000e18 - 1 wei)
7. User calls vote.reset on the high-value NFT. Since its value is lower than the current balance of the user, the user's balance will not be reduced. (1000e18 - 1 wei < 1000e18)
8. Repeat steps 5-7 for all available gauges


In the end the user has not voted with any of the NFT's. Despite this, the user has a balance in all gauges. The user can then send the high-value NFT to his other wallet, where he has such low-value NFTs set from last week and repeat this attack endlessly. In the end, the user can have an arbitrary high balance in all bribes, therefore getting all of the rewards for themselves. Furthermore, since the balance will be spread out across multiple wallets and none of them will have a suspiciously high balance, this could go unnoticed for long time.

** Impact
Adversary can steal all rewards allocated for the upcoming week. Under some conditions and assumptions, this could potentially remain unnoticed for a prolonged time frame.** 


**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
