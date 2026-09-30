# [M] M-13 | exec Should Have whenNotPaused

## Summary
Severity: Medium
Contest weight: 0.0490
Dataset id: 2576
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing pause enforcement on the exec function of the PositionManager contract. The contract implements a global pause mechanism that is intended to stop all state‑changing operations when the protocol is paused, and most functions such as borrow, addToken and removeToken correctly include the whenNotPaused modifier. However, exec, which can forward arbitrary calls on behalf of the contract, does not contain this guard. As a result, an attacker or any caller can invoke exec while the contract is in a paused state and cause the contract to execute external calls, potentially moving tokens, altering positions or performing other privileged actions that the pause was meant to block. The root cause is an oversight in the access‑control design: the pause check was not applied to a function that effectively bypasses the intended safety barrier. Exploitation is straightforward – once the contract is paused, the attacker simply calls exec with crafted parameters to trigger a delegatecall or call to a target contract, thereby executing the unwanted action. The impact includes loss or unauthorized transfer of user funds, unexpected changes to positions, and a breach of the protocol’s guarantee that pausing halts all critical operations. This condition occurs only when the contract is paused; in normal operation the missing guard may go unnoticed because exec is expected to be used for legitimate governance actions. Users, token holders, and the protocol as a whole are affected because the pause is a core risk‑mitigation tool. The issue was discovered during a manual audit that compared the modifiers applied to each external function. It can be hard to notice because the pause flag is a global variable and developers may assume that all external functions inherit the same protection, overlooking functions that perform low‑level calls. To remediate, the exec function should be annotated with the whenNotPaused modifier, and a systematic review of other functions such as transfer should be performed to ensure they respect the pause state. Adding the modifier restores the intended invariant that no state‑changing or fund‑moving operation can occur while the protocol is paused, aligning the contract’s behavior with its security model and user expectations that a paused contract is inert.

## Recommendation
Include the whenNotPaused modifier in the exec function. Additionally, reassess other functions like transfer to determine if they should be permitted when paused.
