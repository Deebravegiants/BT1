# [M] Missing whenNotPaused modifier

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-connext
Published: 2022-06-19
Source: https://github.com/code-423n4/2022-06-connext-findings/issues/175
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-connext/blob/b4532655071566b33c41eac46e75be29b4a381ed/contracts/contracts/core/connext/facets/StableSwapFacet.sol#L279-L286


# Vulnerability details

## Impact
In `StableSwapFacet.sol`, two swapping functions contain the `whenNotPaused` modifier while `swapExactOut()` and `addSwapLiquidity()` do not. All functions to swap and add liquidity should contain the same modifiers to stop transactions while paused. 

## Proof of Concept
***Example with modifier***
```
  function swapExact(
    bytes32 canonicalId,
    uint256 amountIn,
    address assetIn,
    address assetOut,
    uint256 minAmountOut,
    uint256 deadline
  ) external payable nonReentrant deadlineCheck(deadline) whenNotPaused returns (uint256) {
```

***Examples without modifier***
```
  function swapExactOut(
    bytes32 canonicalId,
    uint256 amountOut,
    address assetIn,
    address assetOut,
    uint256 maxAmountIn,
    uint256 deadline
  ) external payable nonReentrant deadlineCheck(deadline) returns (uint256) {
```

and

```
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-06-connext-findings/issues/175_
