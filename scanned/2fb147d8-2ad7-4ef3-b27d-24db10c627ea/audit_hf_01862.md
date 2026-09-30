# [M] M-7 Conditions' order has impact

## Summary
Severity: Medium
Contest weight: 0.0450
Dataset id: 10371
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a logic flaw where the evaluation of protocol conditions depends on the sequence in which they are stored and checked. The root cause is that the condition manager contracts iterate over a list of conditions and stop processing as soon as a failing condition is encountered, without guaranteeing that all required checks are performed regardless of order. An attacker who controls or can influence the ordering of conditions – typically the contract owner – can deliberately place a benign condition before a critical one, causing the critical check to be skipped when the earlier condition passes. This can be exploited by submitting a transaction that satisfies the first condition while the second, more restrictive condition is never evaluated, allowing actions that should be prohibited, such as unauthorized withdrawals, parameter changes, or execution of privileged functions. The impact is that the protocol’s security guarantees are weakened: users may lose funds, the protocol may behave contrary to its specifications, and the system becomes less flexible because any future addition of conditions must consider ordering constraints. The issue manifests whenever the condition manager’s check function is called, which is during every operation that relies on condition validation – for example, order placement, settlement, or admin actions. All participants that rely on the correctness of these checks – traders, liquidity providers, and the protocol itself – are potentially affected. The flaw was discovered during a manual audit where the reviewers noticed that the condition verification loop used a simple for‑loop over an array and that the order of entries altered the outcome, a pattern that is easy to overlook because the code appears to perform all checks at a glance. The problem is subtle because the contract may work correctly with the current default ordering, masking the risk until an owner intentionally reorders conditions. To remediate, the condition checking architecture should be redesigned to be order‑independent: conditions should be stored in a mapping or set and evaluated independently, or the loop should aggregate results of all conditions before deciding, ensuring that every required rule is enforced regardless of how they are arranged. This change restores the intended security model and prevents owners from bypassing critical checks through manipulation of condition order.

## Recommendation
We recommend redesigning the conditions check architecture to make its order independent.
