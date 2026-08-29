# [M] Potential DOS in `delegate_compound` Function

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-17
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/30
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x588cdd2499992876146eabbb7a4c9f876c858fc05954ae02d5f28df87a0c921b
**Severity:** medium

**Description:**
**Description:** The `delegate_compound` function iterates over all agents and calls `compound` on them. However, if there is a revert in one of the agents' compound calls, the entire compound function will revert. The `nomination_agent::compound` function might revert if an agent has not yet joined the nomination pool or has already reaped from it.

**Impact:** DOS vulnerability in the `compound` function.

**Scenario:**
If one of the agents has not yet joined the nomination pool or has already reaped from it, the `delegate_compound` function will revert.

**Revised Code File (Optional):**

2 ways:

first:

```diff
         for (i, a) in agents.into_iter().enumerate() {
+
             match call_compound(a.address, incentive_percentage_) {
+                // Check if the agent has joined the nomination pool and then call compound for that agent
                 Ok((compound_amount, incentive_amount)) => {
                     debug_println!("Compounded {} to agent #{}", compound_amount, i);
```

By adding a check to ensure that the agent has joined the nomination pool before calling the `compound` function, potential DOS vulnerabilities in the `delegate_compound` function can be mitigated.

second:

just like [withdraw](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/c9bdc853b18c305de832307b91a9bca0f281f71e/src/nomination_agent/lib.rs#L113) function, do not revert the call.
