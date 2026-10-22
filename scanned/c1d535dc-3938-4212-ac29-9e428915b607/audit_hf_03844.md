# [M] Lack of rebalance rate limiting allow operator to drain vault

## Summary
Severity: Medium
Contest weight: 0.2040
Dataset id: 20095
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Operators of Arrakis vaults are constrained by the checks defined in
SimpleManager.sol, these checks prevent them from causing too much of a fund
loss on a single rebalance call (check univ3 pool price deviation, enforce minimum
swap slippage parameters).
However since there is no rate limiting for an operator to call rebalance on
SimpleManager, an operator can simply drain the vault by applying the accepted
slippage a hundred times in one transaction.
There are mostly two safety measures for preventing an operator to extract vault
funds when calling rebalance:
• Check pool price deviation for mints: By checking that a pool price is close to
a price given by a chainlink feed, operator is prevented from adding liquidity to
a pool at a really unfavorable price, and backrun later to extract vault funds
• Check slippage parameters for swap (_checkMinReturn): By checking that a
minimum amount of tokens is returned to the vault after the swap, it is
preventing the operator to swap tokens at a too unfavorable price. Min
amount out enforced in ArrakisV2:
rrakisV2.sol#L341-L363
As stated by the sponsor, in a public trustless setup, these slippage parameters
should be restricted to ~1%.
However since an operator is not rate limited for the number of calls she can do on
SimpleManager.rebalance, she can simply call it multiple times in a very short
timespan, extract an arbitrarily large share of vault funds.
Vault funds can be drained by a malicious operator.

## Recommendation
Enforce a rate limiting policy to the number of calls which can be made to
SimpleManager's rebalance, or even better enforce a rate limit on loss of funds
which can occur due to rebalances (by evaluating totalUnderlyingWithFees before
and after the execution for example).
