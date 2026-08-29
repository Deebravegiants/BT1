# [H] Changing A could allow an attacker to withdraw huge token balances when the change happens

## Summary
Severity: High
Chain: Smart contract
Component: Common--Stableswap
Published: 2024-08-01
Source: https://github.com/hats-finance/Common--Stableswap-0xd4d9a2772202ce33b24901d3fc94e95a84b37430/issues/39
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x26d1f0c46950585d0f44fa6f68fe5b97384ef99916bd9dfd68ab60461e5c2495
**Severity:** high

**Description:**
**Description**\
Stableswap pools have an amplicifation coefficient(A) that can be adjusted depending on the peg of the stablecoins in the pool and the needed liquidity concentration. This can happen after a pool is deployed when there is not sufficient concentration or when the stablecoin peg has been changed to allow better trading.

An admin can schedule changing of A with the `set_amp_coef` function and can set a valid and reasonable increase or decrease of A, which could expose the pool to a loss. 


**Attack Scenario**\
Check extremely detailed report of the vulnerabilty here - https://medium.com/@peter_4205/curve-vulnerability-report-a1d7630140ec

This issue is in scope because even an honest contract owner can make too big of changes to A and the recommended step in the article is 0.1% per block, which wouldn't be feasible to handle manually.
**Attachments**

1. **Proof of Concept (PoC) File**

Any change of A(especially downward changes) exposes the pool to a potential loss, as described here. An attack scenario would be an attacker detecing when the admin makes a change to A, sandwiching the transaction in-between in the following scenario: 
1. flashloan to imbalance the pool 
2. change A transaction
3. swap in the reverse direction, make a profit and cause a loss to the AMM token inventory, as described in "Loss-Making Updates to A" in the referenced article

https://medium.com/@peter_4205/curve-vulnerability-report-a1d7630140ec

2. **Revised Code File (Optional)**
A ramping up of A, which is now implemented in StableSwap Curve contracts should be implemented to gradually change A - https://github.com/curvefi/curve-stablecoin/blob/master/contracts/Stableswap.vy#L1061
