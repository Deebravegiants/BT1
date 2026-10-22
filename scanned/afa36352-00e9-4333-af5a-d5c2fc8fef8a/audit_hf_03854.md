# [M] It's dangerous for makers to set token deci-

## Summary
Severity: Medium
Contest weight: 0.0252
Dataset id: 20112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An improper handling of token decimal precision in the DODO V3 swap contract allows a maker to specify an arbitrary decimal value that is stored and later used for amount calculations without any validation. The contract trusts the maker‑provided decimal field and records it directly, bypassing the standard ERC‑20 decimals() query. Because the swap logic multiplies or divides token amounts based on this unchecked decimal, a mismatched or deliberately incorrect value causes the contract to transfer either more or fewer tokens than the amount the taker expects. The vulnerability manifests whenever a maker creates a new pool or updates the pool parameters and supplies a decimal that does not match the actual token's precision. An attacker controlling the maker role can set the decimal to a higher number, causing the contract to over‑credit the taker and later drain the pool, or set it lower to under‑pay the taker, effectively stealing funds. From a user’s perspective the symptom is a missing or unexpectedly reduced balance after a swap, or conversely receiving an unusually large amount that later disappears when the pool is settled. The issue was discovered during a manual audit that compared the contract’s stored decimal variable against the token’s on‑chain decimals() value and noted the absence of any check. Because the contract does not emit explicit warnings and the arithmetic still succeeds, the bug can be hard to notice unless the swap results are audited against expected token precision. This class of bug belongs to input‑validation and arithmetic‑precision errors, where external parameters that influence financial calculations are not verified. The proper fix is to retrieve the token’s official decimal value via the ERC‑20 interface and enforce that the stored decimal matches it, or to eliminate the user‑supplied decimal entirely and compute amounts using the token’s native precision. Ensuring that the decimal used in all amount calculations reflects the true token precision restores the accounting invariants of the protocol and prevents funds from disappearing or being mis‑allocated.

## Recommendation
No recommendation available
