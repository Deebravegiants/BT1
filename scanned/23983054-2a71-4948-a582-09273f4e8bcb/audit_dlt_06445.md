# [M] Nomination Agents Linked to Pools in Destroying or Blocked State Cause Revert in Compound and Stake Functions

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-20
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/51
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x21f09c4ad7f9657359133b89c249d647c2c4039a13218fdd168db29ec8e97f5d
**Severity:** medium

**Description:**
**Description**
Nomination agents that are linked to pools in a destroying or blocked state will cause the `compound` and `stake` functions to revert. This is because any attempt to bond extra or join these pools will fail.

**Attack Scenario**
If one of the pools transitions to a destroying or blocked state, any attempt to bond extra or join the pool will revert, causing the `compound` and `stake` functions to fail. This leads to a denial of service (DoS) for these functions.

**Impact**
Denial of service (DoS) in `stake` and `compound` functions, preventing users from staking or compounding their funds.

**Revised Code File (Optional)**
To prevent this issue, we should check the state of each pool associated with a nomination agent before attempting to bond extra or join. If the pool is in a destroying or blocked state, the function should skip that agent.
