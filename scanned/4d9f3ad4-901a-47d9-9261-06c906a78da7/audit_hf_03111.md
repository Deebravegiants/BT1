# [M] Pausing functionality does not work

## Summary
Severity: Medium
Contest weight: 0.0478
Dataset id: 17545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is that the vesting contracts inherit the OpenZeppelin PausableUpgradeable module and apply the whenNotPaused modifier to critical functions, but they do not expose any external pause or unpause functions that invoke the internal _pause/_unpause hooks. As a result, the contract owner (or any authorized role) is unable to transition the contract into a paused state. The root cause is the omission of public pause/unpause wrappers after inheritance, which leaves the pause mechanism dead code. Because the modifier checks a paused flag that can never be set, the contract will continue to execute vesting releases even when the protocol announces an emergency pause. An attacker does not need to trigger the bug directly; the real risk is that the protocol cannot halt token distribution in response to a discovered vulnerability, market manipulation, or regulatory request. This may lead to funds being released to beneficiaries at times that the protocol intended to block, breaking accounting assumptions and potentially exposing users to loss or unfair advantage. The issue manifests whenever the contract is deployed with the current code and the owner attempts to call pause() – the call fails because no such function exists, yet the UI may still display a “paused” toggle based on the inherited interface. Users therefore experience a mismatch: they expect vesting to stop, but tokens continue to vest, leading to unexpected balance changes. The problem was identified during a manual audit that inspected the inheritance hierarchy and noticed the absence of external pause controls. It can be hard to notice because the contract compiles without errors and the PausableUpgradeable base class is present, giving a false sense of safety. The correct remediation is to add public (or onlyOwner‑protected) pause and unpause functions that forward to the internal _pause and _unpause methods, and to ensure that any UI reflects the actual paused state. This restores the intended emergency stop capability and aligns the contract’s behavior with its business logic and user expectations.

## Recommendation
If pausing functionality is required, add public pause and unpause functions that call PausableUpgradeable’s internal _pause/_unpause functions. Confirmed
