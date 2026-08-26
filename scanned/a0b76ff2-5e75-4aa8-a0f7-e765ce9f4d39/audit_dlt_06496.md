# [M] Complete takeover of `AUT_EXT_VotingRoles_v1` due to low threshold allowed

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/67
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x33c153cb6f9e2583a64bc176279ee12287eff36f9d273fcec7d38cfb4001a98e
**Severity:** medium

**Description:**
## Impact
- Complete takeover of the voting role manager contract
- Unauthorized execution as a module on the whole orchestrator system bypassing `onlyModule` restrictions

## Description
The `AUT_EXT_VotingRoles_v1` module allows voting and arbitrary execution within the respective deployed `Orchestrator_v1` system and modules. The problem is there is no minimum `threshold` enforced. While this might not seem like a problem, it can become serious when the `threshold` is set to zero or one because any `voter` can decide to remove all other `voters`.

## Proof of concept
### `removeVoter` takeover
1. Voting management module is initialized with Alice, Bob and Charlie as voters and a threshold of one
2. Charlie decides that he will take sole ownership of the voting via removing the other voters via `createMotion(address(this), (removeVoter(alice), removeVoter(bob)))`  (pseudocode)
3. Even though Alice and Bob votes against the motion, Charlie did vote in favor
4. This means the `requiredThreshold` has been reached in `executeMotion()`  and he can execute it when the voting phase has ended

## Recommendation
Consider to enforce a minimum threshold of two voters (otherwise the module is useless anyway e.g. if the orchestrator owner is the sole voter) in `init()` and `setThreshold()` functions to prevent malicious takeover of the module.
