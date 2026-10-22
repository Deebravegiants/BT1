# [H] SQDF-1 | Winner Can Be Changed

## Summary
Severity: High
Contest weight: 0.0535
Dataset id: 16200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a mutable result flaw that allows the declared winner of a betting event to be altered after the event has been marked as finished. The root cause is that the contract’s reportResult function does not record whether a result has already been submitted, nor does it enforce a single‑time update. Because the function lacks a guard flag or a check that the result is immutable once set, a malicious oracle can invoke reportResult repeatedly after the event closure and flip the winning side at will. An attacker can exploit this by calling reportResult with a different outcome each time, causing the contract’s internal winner variable to be overwritten. The impact is that payouts may be redirected to the attacker or to an unintended party, users who originally won may lose their expected reward, and the overall accounting of the protocol becomes unreliable. This condition occurs whenever the event lifecycle reaches the finished state but the contract does not lock the result, meaning any entity with permission to call reportResult (typically the oracle) can continue to modify it. All participants who placed bets on the event are affected because the final settlement may not reflect the true outcome, leading to lost or incorrectly distributed funds. The issue was discovered during a manual audit that identified the missing state‑change protection. It can be hard to notice because the function may appear to be called only once in normal operation, and there may be no explicit event emitted to signal a result change, so the problem only surfaces under adversarial repeated calls. The bug belongs to the class of “state‑reentrancy after finalization” or “result tampering” vulnerabilities, where business logic assumes immutability after a certain phase but the code does not enforce it. From a user’s perspective the contract may show that they have won, but later their balance drops to zero or the payout is sent to another address, violating the expectation that a declared winner receives the prize. To remediate, the contract should introduce a boolean flag (e.g., resultReported) that is set the first time reportResult is executed and reject any subsequent calls, or otherwise enforce that the winner can be set only once through access control or commit‑reveal schemes, thereby preserving the integrity of the settlement logic.

## Recommendation
Prevent the result from being changed by using a variable to check if the result was already reported.
