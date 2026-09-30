# [M] Swivel.setFee

## Summary
Severity: Medium
Contest weight: 0.4076
Dataset id: 15625
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the administrative fee‑configuration function of the Swivel protocol. The function is intended to allow an authorized admin to update the four fee denominator values (zcTokenInitiate, zcTokenExit, vaultInitiate, vaultExit) that are stored in a two‑dimensional uint16 array named feenominators. The root cause is a coding mistake: the index parameter supplied by the caller (named i) is never used when writing the new values, and the implementation writes to a hard‑coded position (the zero index of the second dimension) for every update. As a result, calls to setFee do not modify the intended fee entry but repeatedly overwrite only the first slot, leaving the other three slots unchanged. An attacker or honest admin who attempts to change a specific fee will observe that the transaction succeeds, emits an event that appears to reflect a change, yet the underlying fee matrix remains partially incorrect. Exploitation is straightforward – an admin simply invokes setFee with any index, expecting the corresponding fee denominator to be updated, but the contract silently ignores the index and keeps the original values for three of the four fee types. This breaks the business logic that assumes fees can be re‑parameterized after deployment; calculations that rely on the unchanged denominators will produce incorrect fee amounts, potentially causing users to pay higher or lower fees than intended. The impact is most acute for protocol operators and users who depend on accurate fee assessments: a user might expect a reduced withdrawal fee after an admin announcement, but the contract will continue to charge the old fee, leading to surprise costs or loss of competitiveness. The bug manifests only when the setFee function is called – typically during a governance or administration window – and only affects the fee configuration state; it does not directly cause ether or token loss, nor does it open a re‑entrancy or access‑control vector. The issue was discovered during a manual code audit when reviewers noticed that the parameter i was never referenced in the assignment statement, and that the resulting state change did not match the emitted event. Because the function appears to succeed and emits a misleading event, the problem can be hard to notice in production unless the fee values are explicitly read after each change or unit tests verify proper indexing. To resolve the issue, the assignment should be rewritten to use the supplied index when updating the array (for example, feenominators[i] = d[x];) so that each fee denominator is correctly overwritten. Conceptually, the fix restores the intended mutable fee‑parameter pattern and aligns the on‑chain state with the administrative intent, eliminating the discrepancy between reported and actual fee settings and preventing silent misconfiguration of protocol economics.

## Proof of Concept
[This function](https://github.com/code-423n4/2022-07-swivel/blob/fd36ce96b46943026cb2dfcb76dfa3f884f51c18/Swivel/Swivel.sol#L495) has a parameter “i” for the index of the new fee denomination but it isn’t used during the update.

## Recommendation
[This line](https://github.com/code-423n4/2022-07-swivel/blob/fd36ce96b46943026cb2dfcb76dfa3f884f51c18/Swivel/Swivel.sol#L507) should be modified like below.

```solidity
feenominators[i[x]] = d[x];
```

Given this allows us to change fees post initialization, and doesn’t lead to the leakage of value or loss of funds, but a potential issue for admins solely (in a rare edge case where fees would even need to be changed), I might consider this low risk?

I agree with the warden here given that this is an incorrect implementation of the intended functionality. The warden’s suggestion shows that the function was not working as intended; if in production, for instance, this was not caught then calls to `setFee` would not work as intended and not set any fees across the markets. Instead, it would only populate the zero index of the 2nd-demensional array `uint16[4] public feenominators;` losing these values `[zcTokenInitiate, zcTokenExit, vaultInitiate, vaultExit]` and breaking functionality.

Yeah I was kind of on the fence on this one thinking the method wouldn’t impact the current feenominators in the way you’ve stated, but because it actually could have an impact, and the event itself also would be misleading, removing the disagreement.

**[robrobbins (Swivel) resolved](https://github.com/code-423n4/2022-07-swivel-findings/issues/117#issuecomment-1208525682):**

Addressed: <https://github.com/Swivel-Finance/gost/pull/419>.
