# [M] BRF-1 | Accidental Magniﬁcation

## Summary
Severity: Medium
Contest weight: 0.0407
Dataset id: 4055
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an arithmetic inconsistency between the distribution and withdrawal phases of the earnings logic. During the distribute function the contract multiplies each user’s earned amount by a distribution rate (disRate) to calculate the amount that should become claimable. However, when a user later calls withdraw, the contract does not apply a corresponding divisor that would reverse the earlier multiplication. As a result the value stored in user.earned is effectively magnified, causing the contract to transfer more tokens than the user originally earned. The root cause is the missing divisor in the withdraw routine, which breaks the invariant that the product of earned and disRate should be neutralised before payout. An attacker can exploit this by triggering a distribution (or relying on an existing one) and then withdrawing the inflated amount, repeatedly draining the pool because each withdrawal removes a larger slice than intended. The impact includes loss of protocol funds, negative pool balances, and a breach of accounting assumptions that earned balances reflect actual entitlement. The condition occurs whenever distribute has been executed and a subsequent withdraw is performed; any user can be affected, but a malicious actor can amplify the effect. The issue was discovered during a manual audit that compared the arithmetic in both functions and noticed the mismatch. It may be hard to notice because the UI often shows the earned amount before multiplication, so users see a correct figure while the contract sends a higher amount, making the bug appear as a bonus rather than a flaw. To fix the problem the contract should either store the raw earned amount and apply disRate only at withdrawal, or introduce a divisor in withdraw that exactly reverses the earlier multiplication, ensuring that the transferred amount equals the intended share. This class of bug belongs to inconsistent state transformation or mismatched scaling factors, which can lead to unintended fund amplification and break the protocol’s financial integrity.

## Recommendation
Add a divisor for the disRate and use it to adjust user.earned values in either the distribute or withdraw functions as needed.
