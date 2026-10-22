# [H] MJR-1 Reentry in withdrawAll

## Summary
Severity: High
Contest weight: 0.0197
Dataset id: 10864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the execution of the withdrawAll function in the PoolingStakingContractV2, the contract performs an external call to a token or workerOwner contract before it updates its internal accounting variables. Because the external call can trigger a fallback or ERC777 hook, a malicious token or a compromised workerOwner can invoke withdrawAll again before the original call finishes. This re‑entrancy allows the attacker to repeat the withdrawal logic while the contract still believes the caller’s balance is unchanged, leading to multiple payouts from the same stake. The vulnerability appears only when the caller controls a contract that implements a callback invoked by the transfer, and when the contract’s state‑change statements are placed after the external call (line 247). From a user’s perspective the function is expected to return the full amount of their stake and rewards once, but an attacker can cause the contract to send additional funds, effectively draining the pool or corrupting accounting. The issue was discovered during a manual audit by MixBytes, who noted that the ordering of operations violates the checks‑effects‑interactions pattern and therefore permits re‑entrancy. The problem can be subtle because the external call may succeed silently and the contract does not emit an explicit warning before the state is altered, making the bug easy to overlook in testing. To remediate the flaw the contract should move all token transfers to the end of the function, apply the checks‑effects‑interactions pattern, and optionally use a re‑entrancy guard modifier. By ensuring that the internal balance is updated before any external call, the contract prevents a malicious callback from re‑entering the function and preserves the intended accounting guarantees. This class of bug is commonly known as a re‑entrancy vulnerability and violates the fundamental assumption that a contract’s state is immutable during an external call.

## Recommendation
Put transfers as the last statements of the method.
