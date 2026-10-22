# [M] Missing `whenNotPaused` modifier

## Summary
Severity: Medium
Contest weight: 0.5850
Dataset id: 11378
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[StableSwapFacet.sol#L279-L286](https://github.com/code-423n4/2022-06-connext/blob/b4532655071566b33c41eac46e75be29b4a381ed/contracts/contracts/core/connext/facets/StableSwapFacet.sol#L279-L286)  

In `StableSwapFacet.sol`, two swapping functions contain the `whenNotPaused` modifier while `swapExactOut()` and `addSwapLiquidity()` do not. All functions to swap and add liquidity should contain the same modifiers to stop transactions while paused.

## Proof of Concept
**_Example with modifier_**
```solidity
function swapExact(
  bytes32 canonicalId,
  uint256 amountIn,
  address assetIn,
  address assetOut,
  uint256 minAmountOut,
  uint256 deadline
) external payable nonReentrant deadlineCheck(deadline) whenNotPaused returns (uint256) {
```

**_Examples without modifier_**
```solidity
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
```solidity
function addSwapLiquidity(
  bytes32 canonicalId,
  uint256[] calldata amounts,
  uint256 minToMint,
  uint256 deadline
) external nonReentrant deadlineCheck(deadline) returns (uint256) {
  return s.swapStorages[canonicalId].addLiquidity(amounts, minToMint);
}
```

## Recommendation
Add the `whenNotPaused` modifier to all functions that perform swaps or liquidity additions.

Resolved by: [connext/nxtp@1dd5559](https://github.com/connext/nxtp/commit/1dd55597359bdda56fc7b62d9e5a31c6b0faf9bc)

I think this makes sense to add!
