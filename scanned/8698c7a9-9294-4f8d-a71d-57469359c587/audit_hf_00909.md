# [H] `InterestRateStrategyV1` ownership can be hijacked

## Summary
Severity: High
Contest weight: 0.5575
Dataset id: 2717
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Ownable.sol#L84-L85](https://github.com/Vectorized/solady/blob/9298d096feb87de9a8873a704ff98f6892064c65/src/auth/Ownable.sol#L84-L85)

```solidity
/// @dev Override to return true to make `_initializeOwner` prevent double-initialization.
function _guardInitializeOwner() internal pure virtual returns (bool guard) {}
```

When utilizing Solady's `Ownable` contract with an upgradable contract, `_guardInitializeOwner` must be overridden to return `true` as communicated in the dev comment above. `InterestRateStrategyV1` is upgradable but does not do this, allowing the contract ownership to be hijacked. Consequences of this could be malicious upgrades to apply large amounts of interest to positions to liquidate all positions and the like.

## Recommendation
`_guardInitializeOwner` should be overridden to return `true`.
