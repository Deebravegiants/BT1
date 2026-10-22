# [M] Strict initialSharePrice checks

## Summary
Severity: Medium
Contest weight: 0.3982
Dataset id: 7267
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC4626Hyperdrive and StethHyperdrive constructors check that the provided initial- SharePrice exactly matches the current share price of the yield source:
```solidity
uint256 shareEstimate = _pool.convertToShares(FixedPointMath.ONE_18);
if (
    _config.initialSharePrice !=
    FixedPointMath.ONE_18.divDown(shareEstimate)
) {
    revert Errors.InvalidInitialSharePrice();
}
```
It's easy for the deployment to revert here because estimating the exact share price when the transaction is mined is very hard as the yield sources can accrue new interest every block. Furthermore, the share price of the yield source can usually be manipulated by donating to the vault which allows an attacker to frontrun the deployment with a tiny donation such that the strict equality check fails.

## Recommendation
Consider removing this denial-of-service attack vector. For example, the factory could fetch the current share price and set it on the config instead of the user having to predict and provide it.
