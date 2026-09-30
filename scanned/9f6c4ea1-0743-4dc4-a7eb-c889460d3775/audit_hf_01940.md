# [M] M-2 Incorrect convergence condition

## Summary
Severity: Medium
Contest weight: 0.0217
Dataset id: 10706
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logical error in an approximation routine that determines when the iterative process should stop. The code uses the condition err_mid < 0 to decide convergence, but the correct mathematical condition is err_mid <= 0. Because the algorithm treats a zero error as a non‑convergent state, it can fail to terminate or return an inaccurate approximation when the error term becomes exactly zero. This edge‑case occurs when the computed midpoint error reaches the precise value of zero, which is a legitimate stopping point for many numerical methods. The root cause is an off‑by‑one style inequality that excludes the boundary case, violating the intended convergence invariant. An attacker or a malicious user can deliberately craft inputs that drive the error term to zero, causing the algorithm to either loop indefinitely or produce a result that deviates from the expected value. In a financial protocol, such a mis‑calculation may lead to incorrect pricing, wrong reward distribution, or a refund that is calculated as zero when a user should receive a positive amount. From the user’s perspective the symptom is a missing or zero balance update, a transaction that appears to succeed but yields no payout, or a UI that shows a “0” result where a non‑zero value is expected. The issue was discovered during a systematic security audit performed by MixBytes, where the auditors exercised boundary inputs and observed that the routine never satisfied the convergence test. Because the condition looks syntactically correct, the bug can be hard to notice without targeted edge‑case testing. The fix is conceptually simple: adjust the convergence check to err_mid <= 0, thereby allowing the algorithm to accept a zero error as a valid termination condition. This change restores the mathematical guarantee of convergence, prevents infinite loops, and ensures that downstream accounting logic receives correct values, preserving the protocol’s financial integrity.

## Recommendation
We recommend altering the convergence condition.
