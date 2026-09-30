# [M] UBT-3 | Payment Pushed Back

## Summary
Severity: Medium
Contest weight: 0.0323
Dataset id: 16195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a privileged‑function manipulation where an account with admin rights can repeatedly invoke the createAllocation routine for the same beneficiary address. Each invocation resets or extends the payoutDay timestamp that governs when the allocated funds become withdrawable. Because the contract does not enforce a single allocation per address or limit the number of times the payout schedule can be altered, the admin can keep pushing the payoutDay further into the future, effectively preventing the intended recipient from ever meeting the withdrawal condition. This occurs whenever the admin role is exercised, typically through a function that accepts an address and an amount and then records a future payout timestamp. The root cause is the lack of state‑guardrails: the contract does not check whether an allocation already exists for the target address, nor does it lock the payoutDay after the first assignment. An attacker with admin privileges can therefore exploit the logic by calling createAllocation in a loop or at regular intervals, each time updating the payoutDay to a later block time. The impact is that users who are supposed to receive a payout see their expected balance remain locked, often appearing as a zero or unchanged amount in the UI, despite the contract holding the funds. From the user’s perspective the interface may show a pending reward that never materialises, violating the business rule that rewards become claimable after a fixed period. The issue was identified during a manual audit that examined privileged functions and noticed that the allocation logic lacked idempotency checks. It can be hard to notice because a single call behaves correctly; only repeated calls reveal the delay effect, which may not be exercised in normal testing. To remediate, the contract should enforce a one‑time allocation per beneficiary, make the payoutDay immutable after the first set, or require a multi‑signature approval for any admin‑level changes that affect payout schedules. Adding explicit checks that prevent overwriting an existing allocation or limiting the number of admin calls per address would close the manipulation vector and restore confidence that allocated funds will become withdrawable as promised.

## Recommendation
Adopt a solution that doesn’t allow such manipulation, or ensure trust via a multi-sig for every
privileged address.
