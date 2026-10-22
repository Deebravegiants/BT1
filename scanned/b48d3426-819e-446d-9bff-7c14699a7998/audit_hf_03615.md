# [M] collectLiquidity

## Summary
Severity: Medium
Contest weight: 0.5647
Dataset id: 19649
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`LP` has only one way to retrieve `token`, first `decreaseLiquidity()`, then retrieve through the `collectLiquidity()` method.

`collectLiquidity()` only has one parameter, `tokenId`.
```solidity
function collectLiquidity(
    uint256 tokenId
) external override nonReentrant returns (uint256 amount0Collected, uint256 amount1Collected) {
    (amount0Collected, amount1Collected) = lps.collectLiquidity(tokenId);
}
```
So `LP` can only transfer the retrieved `token` to himself: `msg.sender`.

This leads to a problem. If `LP` enters the blacklist of a certain `token`, such as the `USDC` blacklist,

Because the recipient cannot be specified (`lps[]` cannot be transferred), this will cause another `token` not to be retrieved, such as `WETH`.

Refer to `NonfungiblePositionManager.collect()` and `UniswapV3Pool.collect()`, both can specify `recipient` to avoid this problem.

## Recommendation
```solidity
function collectLiquidity(
    uint256 tokenId,
    address recipient
) external override nonReentrant returns (uint256 amount0Collected, uint256 amount1Collected) {
```

Good suggestion, recipient should be added here too: <https://github.com/code-423n4/2023-12-particle/blob/main/contracts/libraries/LiquidityPosition.sol#L329>

I would argue this is good design and should not be changed to allow for arbitrary recipients. If a token is blacklisted, and a protocol allows the user to circumvent this blacklist, then they may potentially be liable for the behaviour of this individual. Better to take an agnostic approach and leave it as is unless liquidations are ultimately being limited because of this.

I agree with the judge. We shouldn't facilitate to temper the blacklist. So only acknowledging the issue.
