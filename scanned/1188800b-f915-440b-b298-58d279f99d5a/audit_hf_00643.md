# [M] M-01 | User Can Pass Arbitrary Fee Amount

## Summary
Severity: Medium
Contest weight: 0.0551
Dataset id: 2170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the loan entry point where the borrow function accepts a feeAmount parameter supplied by the caller. Because the contract does not validate that the feeAmount matches the protocol’s expected fee policy, a user can invoke borrow directly and pass any value, including zero. The root cause is the absence of internal enforcement of the fee calculation; the fee is treated as an external input rather than being derived from the borrowed amount or a fixed percentage. An attacker can exploit this by submitting a transaction that calls borrow with feeAmount set to 0, thereby receiving the full loan amount without paying the intended fee. This results in the protocol losing expected revenue, potentially destabilising its economic model and reducing incentives for lenders. The issue manifests whenever a borrower interacts with the contract outside of any higher‑level wrapper that might enforce the fee, i.e., any direct call to borrow. All participants who rely on the fee for correct accounting—such as lenders, protocol treasury, and token holders—are affected because the fee shortfall reduces the funds available for distribution or reserve. The flaw was discovered during a manual audit that examined the loan interface and noted that the feeAmount argument was not constrained. It can be difficult to notice because the function signature appears to accept a fee, and the UI may display a fee field, leading developers and users to assume the fee will be collected automatically. However, the contract logic never checks the value, so a zero fee passes silently. To remediate, the contract should compute the fee internally based on a predefined percentage of the borrowed amount or enforce that the supplied feeAmount equals the expected calculation, rejecting any transaction where the fee is missing or incorrect. This aligns the implementation with the intended business rule that every loan must incur a fee, restoring proper accounting and protecting protocol revenue.

## Recommendation
Add validation on the expected feeAmount for K33. Alternatively, consider tieing feeAmount to a fixed percentage of the borrowed/liquidated amount rather than letting the caller supply an arbitrary fee, implement a fixed percentage model (e.g., feeAmount = (borrowedAmount * feePercentage) / 1e18).
