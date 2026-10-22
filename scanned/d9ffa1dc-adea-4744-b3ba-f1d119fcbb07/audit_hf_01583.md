# [H] MJR-6 Broken account must be deleted

## Summary
Severity: High
Contest weight: 0.0126
Dataset id: 8492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a broken account state that persists when a token transfer initiated by the protocol fails and is reverted. The root cause is the absence of cleanup logic after a failed transfer; the contract does not delete or deactivate the user’s accounting record even though the underlying token operation did not succeed. An attacker or any user can trigger a transfer that reverts – for example by using a token that rejects the transfer, has insufficient allowance, or contains a custom require that fails – and the protocol will leave the account entry in its internal ledger unchanged. Because the account is still considered active, subsequent operations that rely on the account’s balance or debt position may behave incorrectly, leading to accounting mismatches, inability to withdraw or claim rewards, and potentially a denial‑of‑service condition where the protocol cannot process further actions for that user. From the user’s point of view the symptom is that after attempting a withdrawal or reward claim the UI shows no change, the balance appears unchanged or zero, and the expected funds never arrive. The issue was discovered during a manual security audit by MixBytes, which noted that the code path at the point where token transfers are performed does not include a branch to remove the account when the external call reverts. The bug is subtle because the transaction itself does not revert – only the internal token call does – so the overall transaction may appear successful while the internal state is left inconsistent. To remediate the problem the contract should incorporate explicit error handling: if a token transfer returns false or throws, the protocol must either roll back the entire operation or, if partial state changes are acceptable, delete or deactivate the affected account and emit an event indicating the cleanup. This ensures that the accounting model remains sound, users do not lose access to their funds, and the protocol’s financial invariants are preserved. The class of bug is a state‑inconsistency after external call failure, commonly referred to as improper cleanup of stale accounts or broken accounting entries.

## Recommendation
We recommend to delete account in case some transfers are reverted.
