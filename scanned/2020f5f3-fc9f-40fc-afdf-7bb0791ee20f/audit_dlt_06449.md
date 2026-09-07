# [M] Inconsistency in Nomination Pool Joining Logic

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-17
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/29
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x588cdd2499992876146eabbb7a4c9f876c858fc05954ae02d5f28df87a0c921b
**Severity:** medium

**Description:**
**Description:** The `nomination_pools` module uses the `staked` variable to determine whether an agent can join a nomination pool. However, the reduction of `self.staked` occurs in the `start_unbond` function, not in the `withdraw_unbonded` function. This leads to an inconsistency where an agent may attempt to rejoin a pool after being unbonded but not withdrawn(the agent reaped in the withdrawn step, not the unbound step), causing a potential denial-of-service (DOS) vulnerability in the stake function.

**Impact:** DOS vulnerability in the stake function

**Scenario:**
1. An agent initially joins a nomination pool.
2. The agent is unbonded but not withdrawn, resulting in `staked = 0`.
3. The agent attempts to rejoin the pool in the next deposit and it reverts.

**Revised Code File (Optional):**
```diff
         admin: AccountId,
         pool_id: u32,
         staked: u128,
+        joined: u128
     }
 
     #[derive(Debug, PartialEq, Eq, scale::Encode, scale::Decode)]
@@ -41,6 +42,7 @@ mod nomination_agent {
                 admin: admin_,
                 pool_id: pool_id_,
                 staked: 0,
+                joined: 0
             }
         }
 
@@ -52,7 +54,8 @@ mod nomination_agent {
             if Self::env().caller() != self.vault {
                 return Err(RuntimeError::Unauthorized);
             }
-            if self.staked == 0 {
+            if self.joined == 0 {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/29_
