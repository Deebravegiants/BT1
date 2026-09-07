# [M] Minimum Stake Not Checked for Each Nomination Agent

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-19
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/48
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x109b9c70352753d22fcdd5f5ccae2d8b22a9b8be3293ebcf259c396fbed7008e
**Severity:** medium

**Description:**
**Description**
The minimum stake that can go through a nomination pool is 10 AZERO, and the `stake` function contract checks for this value as shown [here](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/c9bdc853b18c305de832307b91a9bca0f281f71e/src/vault/lib.rs#L217). The issue is that this check should be done for each agent, not just the input stake amount.

**Impact**
The lack of this check can cause the `stake` function to fail, leading to a Denial of Service (DoS) scenario when staking amounts that are split between multiple agents fall below the minimum required stake for each agent.

**Proof of Concept (PoC), Scenario**
Each agent's bond amount is calculated in the `delegate_bonding` function. Consider the following scenario:

1. A user sees the minimum stake is 10 AZERO.
2. There are two nomination agents, each with a weight of 1, so each agent will receive 5 AZERO from a 10 AZERO stake.
3. When the user stakes 10 AZERO, the initial check passes, but the call to each nomination agent reverts with a `CallRuntimeFailed` error because the amount each agent receives (5 AZERO) is below the minimum stake requirement.

**Revised Code File (Optional)**
Instead of checking the user's stake amount, find the lowest amount that will go to an agent and check that against the minimum stake.
