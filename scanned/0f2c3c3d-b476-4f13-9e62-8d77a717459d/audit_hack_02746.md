# [M] EulerStrategy: Too much withdrawn when used with AlphaBetaSplitter under some circumstances

## Summary
Severity: Medium
Reporter: Lambda
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L46
Type: audit-issue

## Details
# EulerStrategy: Too much withdrawn when used with AlphaBetaSplitter under some circumstances

## Summary
`AlphaBetaSplitter` implicitly assumes that `withdrawAll` returns exactly the balance that is returned by `_balanceOf`. This is not always true for `EulerStrategy`.

## Vulnerability Detail
When `_amount` is withdrawn from `AlphaBetaSplitter` and this value is larger than the balance of the first child (which was retrieved earlier with a `_balanceOf` call on the child), `withdrawAll` is called. Then, `_amount - childOneBalance` is withdrawn on the second child. This assumes that the `withdrawAll()` call on the first child in fact returned `childOneBalance`. However, this is not necessarily true for `EulerStrategy` and it can happen that the strategy returns more. This can happen because `EulerStrategy._balanceOf` does not incorporate the USDC that is currently held by the strategy contract (in contrast to e.g. `TrueFiStrategy._balanceOf`, which incorporates this). While it is not incorporated in `_balanceOf`, the additional tokens are still returned in `_withdrawAll`, leading to this discrepancy.

## Impact
Because of this issue, it can happen that more tokens are returned than requested when Euler is used within an `AlphaBetaSplitter`. Let's say that 100,000 USDC are locked in Euler and the strategy contract holds additional 5,000 USDC. We assume that the `EulerStrategy` is the first child of an `AlphaBetaSplitter` and `_withdraw` is called with 105,000 USDC. Then, `_withdrawAll` will be called on `EulerStrategy` (returning 105,000 USDC) and `_withdraw` will be called with 5,000 USDC on the second child, meaning the overall transferred amount is 110,000 USDC and not 105,000 USDC.

## Code Snippet
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L46
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L70
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/splitters/AlphaBetaSplitter.sol#L38

## Tool used

Manual Review

## Recommendation
Check the actual amount that was returned by `_withdrawAll` in `AlphaBetaSplitter`. This value is already returned by all strategies, so refactoring the Splitter to incorporate it should be easy.
