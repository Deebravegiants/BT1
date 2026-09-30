# [M] USDConversions can swap locked funds

## Summary
Severity: Medium
Contest weight: 0.0465
Dataset id: 13995
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the USDConversions component of the yield manager, where DAI tokens that have been locked for a finalized withdrawal can be unintentionally swapped into other USD‑denominated yield tokens. The root cause is that the conversion routine does not verify whether the amount being exchanged includes any portion of the locked balance; the library that performs the swap has no visibility into the locked‑fund accounting and therefore cannot prevent the operation. An attacker or any user with permission to invoke the convert function can trigger a swap after a withdrawal has been marked as finalized but before the user actually claims the funds. By moving the locked DAI to a different token, the protocol’s internal accounting no longer has the expected DAI available for the pending withdrawal, causing the subsequent withdrawal call to revert or return zero. From the user’s perspective the UI may show a successful withdrawal request, yet the transaction fails or the user receives no tokens, leading to a perception that funds have disappeared or that a refund is missing. This issue manifests only in the narrow window between finalization of a withdrawal and the actual claim, and it affects any participant who has a pending finalized withdrawal as well as the overall protocol’s financial integrity. The problem was identified during a manual audit by Spearbit, who noticed that the USDConversions library lacks a guard against operating on locked balances, a subtle flaw that can be missed because the conversion itself succeeds and only the later withdrawal exhibits the symptom. To remediate the issue the conversion function should include a check that reverts when the amount to be swapped overlaps with any locked balance, or the design should separate locked and free balances so that swaps are only permitted on free assets. Implementing such a guard restores the accounting invariant that finalized withdrawals must be fully redeemable, preventing users from receiving an empty payout and preserving trust in the protocol’s handling of funds.

## Recommendation
Consider reverting if locked funds are swapped. It should be enough to check this in the USDYieldManager.convert call as other calls to _convert always perform a transfer from the user before (the USDConversions library does not have access to the locked amount).
