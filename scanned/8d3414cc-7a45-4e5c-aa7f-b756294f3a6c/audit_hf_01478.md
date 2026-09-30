# [M] Strategists can’t be removed

## Summary
Severity: Medium
Contest weight: 0.0848
Dataset id: 7848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing revocation mechanism for the strategist role. In the contract a strategist can be approved through an approveStrategist function, but there is no counterpart to set the flag to false. This design flaw means that once an address is granted strategist privileges it retains them for the lifetime of the contract. The root cause is that the access‑control state variable is only ever set to true and never cleared, and no external function is provided to change it. An attacker who obtains the private key of a strategist, or a former team member whose privileges should be withdrawn, can continue to invoke any function protected by the strategist modifier. By repeatedly calling privileged pool‑management functions—such as withdrawing liquidity provider (LP) tokens, adjusting fees, or rebalancing assets—the attacker can siphon funds from the pool. The impact is that liquidity providers may see their deposits disappear, the protocol's capital can be drained, and users lose confidence in the system. The issue manifests whenever a strategist is appointed and later needs to be removed, for example after a role change, key rotation, or suspicion of misconduct; because the contract provides no way to do so, the elevated permissions remain active indefinitely. All participants are affected: LP providers who lose funds, the protocol governance that cannot enforce discipline, and developers who cannot remediate a compromised account. The problem was identified during a manual code review by the auditing team, which noticed the approveStrategist function but could not locate any revocation path. The absence of a revocation function is subtle; the contract otherwise appears functional, so the flaw can be missed unless the reviewer explicitly checks role lifecycle management. The bug belongs to the class of “undeletable privileged role” or “missing access revocation” vulnerabilities, where a contract assumes that permissions can be withdrawn but the code does not support it. From a user perspective, the expected behavior is that a malicious strategist could be stripped of rights, preventing further theft; in reality the strategist remains active, leading to symptoms such as unexpected zero balances, missing refunds, or complete loss of deposited LP tokens. To remediate, the contract should introduce a function that allows the owner or governance to set the strategist flag to false, emit an event when the role is revoked, and preferably use a well‑tested role‑based access control library that supports both grant and revoke operations. This change restores the ability to enforce the principle of least privilege and mitigates the risk of permanent privileged access.

## Proof of Concept
There’s a function to [approve](https://github.com/code-423n4/2022-05-rubicon/blob/main/contracts/rubiconPools/BathHouse.sol#L264) a strategist, but no option to revoke the access.

## Recommendation
Add a function / change the function and allow setting strategist’s access to false.

Low severity, we can add this anytime with a proxy upgrade but still a good function to add.

As per the rulebook (no. 11), upgradeability should not be used as an excuse to reduce the severity of a finding.
