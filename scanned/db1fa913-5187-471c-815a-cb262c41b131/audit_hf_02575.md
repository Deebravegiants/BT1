# [M] swapIdleAndAddToLiquidity may be DoSed

## Summary
Severity: Medium
Contest weight: 0.0617
Dataset id: 13904
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The swapIdleAndAddToLiquidity function allows the rebalancer to input
swapQuantity to swap a certain amount of tokens. Assume that the rebalancer
uses the balance as swapQuantity, that is, he wants to swap all tokens. The
user can withdraw some tokens in advance, which will cause the contract
balance to be less than swapQuantity, and then the swap will fail.

## Recommendation
Take the smaller value of swapQuantity and balance as the swap input.
