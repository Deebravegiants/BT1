# [M] M-9 Royalty parameters are not checked

## Summary
Severity: Medium
Contest weight: 0.0346
Dataset id: 16363
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of missing validation on the royalty parameters that drive the fee calculation for the royalty receiver in the ERC721 implementation. The contract accepts a royaltyRate_ value that is intended to be expressed in basis points (BPS), where the maximum allowed value is the total number of basis points in one hundred percent. Because there is no explicit check that royaltyRate_ does not exceed BPS, a caller can supply a rate larger than the allowed maximum. When the contract later attempts to compute the royalty amount, the oversized rate causes the arithmetic or the payment call to revert, aborting the entire transaction. This can be exploited by a malicious token creator or any party that can set or update the royalty parameters: they can deliberately set royaltyRate_ to a value greater than BPS, causing every subsequent transfer, sale, or mint that triggers royalty payment to fail. From a user perspective the symptoms are transaction reverts, NFTs not being transferred, or sales that appear to succeed but then roll back, often with an error message indicating a failed royalty payment. The impact includes denial‑of‑service for token holders, loss of expected royalty revenue, and a break in the protocol’s accounting assumptions that royalties are always payable. The issue manifests whenever royalty parameters are read – typically during token transfer or sale – and only becomes visible when an out‑of‑range rate is used, which may not be covered by standard test cases. The audit team discovered the flaw during a systematic review of the contract’s financial logic, noting the absence of require statements that enforce royaltyRate_ ≤ BPS. Because the failure occurs deep inside a payment routine, it can be hard to notice without deliberately testing extreme values. The proper remediation is to add explicit checks that enforce the royalty rate to be bounded by BPS and to validate that the royalty recipient address is non‑zero before any payment is attempted. This aligns the implementation with the intended business rule that royalties must be a percentage of the sale price and prevents the contract from entering a state where royalty calculations cause reverts, thereby preserving user expectations that a sale will either complete with correct royalty distribution or fail with a clear, predictable error.

## Recommendation
We recommend adding checks for royalty parameters.
