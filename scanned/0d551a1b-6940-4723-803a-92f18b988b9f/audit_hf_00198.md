# [M] `MochiTreasuryV0.withdrawLock

## Summary
Severity: Medium
Contest weight: 0.0821
Dataset id: 1046
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the treasury contract's withdrawLock() function, which is intended to enforce a lock on token withdrawals when a specific lock flag (often represented as a boolean such as lockCrv) is enabled. However, the implementation does not include any check to verify that the lock is currently active before allowing the function to be executed. Consequently, callers can invoke withdrawLock() even after the protocol has toggled the lock flag, resulting in withdrawals that should have been prohibited. This omission originates from a missing require statement that would normally revert the transaction if the lock flag indicates a locked state. An attacker, or any user aware of the missing guard, can trigger withdrawLock() during a period when the lock is supposed to be in effect, thereby extracting tokens from the treasury or re‑locking tokens in a malicious manner. The impact is that funds intended to be frozen may be moved unexpectedly, leading to potential loss of assets for token holders and compromising the protocol's accounting assumptions about locked balances. The issue manifests whenever the lock flag has been set to true but withdrawLock() is called without restriction; it affects all participants who rely on the lock mechanism for security, including users, the treasury itself, and downstream contracts that assume locked funds remain immobile. The bug was discovered during a formal audit by Code4rena, where the logic of the function was examined and the absence of a lock check was noted. Because the function name suggests a protective operation, developers and auditors might overlook the fact that the actual state is not enforced, making the problem subtle and easy to miss during casual testing. To remediate, the contract should explicitly verify the lock status at the beginning of withdrawLock(), typically with a statement such as require(!lockCrv, "!lock"), ensuring that the function reverts when the lock is active. This change restores the intended business logic: withdrawals should only be possible when the lock is disabled, preserving the integrity of the treasury's locked balances and preventing unexpected fund movement.

## Proof of Concept
* [`MochiTreasuryV0.sol#L40` L42](https://github.com/code-423n4/2021-10-mochi/blob/main/projects/mochi-core/contracts/treasury/MochiTreasuryV0.sol#L40-L42)

## Recommendation
Consider adding `require(lockCrv, "!lock");` to `withdrawLock()` to ensure this function is not called unexpectedly. Alternatively if this is intended behaviour, it should be rather checked that the lock has not been toggled, otherwise users could maliciously relock tokens.

[ryuheimat (Mochi) confirmed](https://github.com/code-423n4/2021-10-mochi-findings/issues/161)
