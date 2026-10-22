# [H] MJR-1 Error while calculating the value

## Summary
Severity: High
Contest weight: 0.0191
Dataset id: 6942
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a scaling error in the price‑per‑share calculation of a yDAI token wrapper. The function that should return the price per full share multiplies the raw share value by the fixed‑point factor 1e18 but fails to divide the result by the same factor before returning it. As a result the reported price is inflated by exactly 1e18 times the correct value. This mistake originates from an incorrect handling of the token’s 18‑decimal precision, a common pitfall when mixing integer arithmetic with fixed‑point scaling. Any contract that relies on this function – for example the flash‑loan borrower implementation that calls getPricePerFullShare at several points – will receive a massively overstated share price and will therefore compute token amounts that are off by the same factor. An attacker or a careless developer can exploit the bug by triggering a transaction that uses the erroneous price to request or repay assets, causing the protocol to transfer far more tokens than intended or to believe a repayment has been satisfied when it has not. The impact includes potential loss of funds, incorrect accounting, and failure of flash‑loan repayment logic, which may leave user balances empty or cause the protocol to become under‑collateralised. The condition occurs every time the price‑per‑share getter is invoked, which in the audited code happens in the CoverFlashBorrower contract at the indicated lines. All participants that interact with the yDAI wrapper – borrowers, liquidity providers, and the protocol itself – are affected because the bug corrupts the fundamental accounting invariant that one share equals a fixed amount of underlying assets. The issue was discovered during a manual security audit performed by MixBytes, who noted the mismatch between the multiplication and the missing division. The bug can be subtle because the returned number is still a valid uint256 and may be used in subsequent calculations that also apply a 1e18 scaling, thereby masking the error until a concrete mismatch in token balances appears. To remediate the problem the getter should either divide the multiplied value by 1e18 before returning it or, alternatively, avoid the unnecessary multiplication altogether and keep the value in its native fixed‑point representation. In broader terms the flaw belongs to the class of decimal‑scaling or unit‑conversion bugs that break financial invariants and lead to erroneous token transfers, refund failures, or balance disappearances.

## Recommendation
It is recommended to fix the error.
