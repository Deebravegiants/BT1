# [M] M-18 The borgMode variable value should be immutable

## Summary
Severity: Medium
Contest weight: 0.0389
Dataset id: 10365
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a contract state variable named borgMode that is intended to represent a fixed operating mode of the protocol. In the current implementation the variable is declared as a regular mutable storage variable and is not marked immutable or constant, nor is its value locked after construction. Because the value can be altered after deployment, the internal permission check performed by the isMethodCallAllowed function, which relies on borgMode to select a set of method constraints, may behave inconsistently. An attacker or any account with access to a function that can modify borgMode (directly or indirectly through a setter, upgradeable proxy, or mis‑configured access control) could change the mode to a less restrictive setting, causing the contract to accept calls that should be rejected. This can lead to unauthorized method execution, potential loss or misdirection of funds, and a breach of the protocol’s business logic that assumes a static mode for accounting and security checks. The issue manifests when the variable is changed at runtime; users may observe that operations which previously reverted now succeed, resulting in unexpected state changes such as balances being altered without explicit user intent, refunds not being issued, or privileged actions being performed by unauthorized parties. The problem was identified during a manual security audit that examined the contract’s state management and discovered that borgMode lacks the immutable keyword and is not protected against post‑deployment modification. Because the variable appears to be a simple configuration flag, the mutability may not be obvious without a detailed code review, making the bug easy to overlook. To remediate, the borgMode value should be fixed at deployment time, for example by declaring it immutable and assigning it only in the constructor, and by removing any functions that could modify it thereafter. This ensures that methodConstraint checks remain consistent throughout the contract’s lifetime, preserving the intended security guarantees and preventing the described unauthorized behavior.

## Recommendation
We recommend fixating the borgMode variable value inside the contract constructor.
