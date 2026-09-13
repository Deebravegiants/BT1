# [H] 5.1.1 UseuncheckedinTickMath.solandFullMath.sol

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Overlay TickMath, Euler TickMath, Overlay FullMath, Euler FullMath
**Description:** Uniswap math libraries rely on wrapping behaviour for conducting arithmetic operations. Solidity
version0.8.0introduced checked arithmetic by default where operations that cause an overflow would revert.
Since the code was adapted from Uniswap and written in Solidity version0.7.6, these arithmetic operations
should be wrapped in anuncheckedblock.
**Recommendation:** Add anuncheckedblock to the following functions inTickMath.solandFullMath.sol:

- getSqrtRatioAtTick()
- getTickAtSqrtRatio()
- mulDiv()
- mulDivRoundingUp()
The Uniswap protocol has a reference implementation for these changes in a branch named 0.8.
**Overlay** : Fixed in commit 1f6a974.
**Spearbit:** Acknowledged.
