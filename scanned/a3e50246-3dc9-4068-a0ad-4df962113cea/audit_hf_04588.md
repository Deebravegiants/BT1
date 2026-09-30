# [M] M-21 | removeLeverage Could Fail For Self-Lending Pairs

## Summary
Severity: Medium
Contest weight: 0.1330
Dataset id: 22191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This bug was reported in a previous audit but does not seem to be fixed (see [https://hackmd.io/@tapir/SyxqzohUA#M-6-Removing-leverage-will-likely-fail-if-the-pod-token-needs-to-be-sold-for-the-borrowed-token-in-a-self-lending-scenario](https://hackmd.io/@tapir/SyxqzohUA#M-6-Removing-leverage-will-likely-fail-if-the-pod-token-needs-to-be-sold-for-the-borrowed-token-in-a-self-lending-scenario)) The issue remains that there is no natural Uniswap V2 market that exists to swap pod tokens for borrowed assets (from FraxlendPair), when the pair is self-lending. Furthermore, during _swapPodForBorrowToken in the removeLeverage flow, the entire amount of pod tokens received is passed as amountInMax for the swap --resulting in zero slippage protection. This could allow an attacker to deploy a pool to take advantage of this scenario and steal all pod tokens from a user.

## Recommendation
Implement proper slippage protection for the swap, and ensure that a healthy Uniswap V2 market exists for the swapping of self-lending pairs.
