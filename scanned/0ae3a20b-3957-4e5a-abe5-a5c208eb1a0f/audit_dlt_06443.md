# [M] Dos in send_batch_unlock_requests function due to invalid range for agent's boned AZERO

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-23
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/61
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xb2f232676b39c9ab75a7783fa00e6d24d2df976858dd3d63f83f1d847d6babf9
**Severity:** medium

**Description:**
**Description**
Each agent must either unbond entirely or maintain at least the minimum required bond (`minimum_stake`) after the `unbond` function. The current implementation in `delegate_unbonding` does not account for this requirement, and if one of the agents reverts in `unbond` function, it will lead to reverting in `send_batch_unlock_requests`. This issue leads to a denial of service (DOS) in the `send_batch_unlock_requests` function due to incorrect calculations in `delegate_unbonding`.

**Impact**
If the `send_batch_unlock_requests` function attempts to unbond an amount that results in an agent's stake being between 0 and 10 AZERO, it will cause the function to revert, leading to a DOS on the `send_batch_unlock_requests` functionality.


**Scenario**
there are 10 agents with a total of 1000AZERO.
a user wants to unstake 200AZERO.
after all, one agent will remain in a 0<<`minimum_stake` range and the function revert.

**Revised Code File (Optional)**
The solution is to check each agent in `delegate_unbonding` to ensure that the remaining staked value after unbonding will either be 0 or at least `minimum_stake`. If the unbonding amount would leave the staked value in the range of 0-10 AZERO, adjust the unbond amount to meet the requirements.
