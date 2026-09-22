# [M] \[M04\] Incorrect event emission

## Summary
Severity: Medium
Source: https://github.com/compound-finance/open-oracle/blob/d0a0d0301bff08457d9dfc5861080d3124d079cd/contracts/Uniswap/UniswapAnchoredView.sol#L241
Type: audit-issue

## Details
The `UniswapWindowUpdate` event of the `UniswapAnchoredView` contract is currently [being emitted in the pokeWindowValues function](https://github.com/compound-finance/open-oracle/blob/d0a0d0301bff08457d9dfc5861080d3124d079cd/contracts/Uniswap/UniswapAnchoredView.sol#L241) using incorrect values. In particular, as it is being emitted [_before_ relevant state changes are applied](https://github.com/compound-finance/open-oracle/blob/d0a0d0301bff08457d9dfc5861080d3124d079cd/contracts/Uniswap/UniswapAnchoredView.sol#L242-L246) to the `oldObservation` and `newObservation` variables, the data logged by the event will be outdated.

Consider emitting the `UniswapWindowUpdate` event _after_ changes are applied so that all logged data is up-to-date.
