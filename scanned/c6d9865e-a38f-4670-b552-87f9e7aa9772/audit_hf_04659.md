# [M] getOracleData() maxExternalDeposit not ac-

## Summary
Severity: Medium
Contest weight: 0.5806
Dataset id: 22401
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In getOracleData() the calculation of maxExternalDeposit lacks consideration for reserve.accruedToTreasury. This leads to maxExternalDeposit being too large, causing Treasury.rebalance() to fail.
In getOracleData()
```solidity
function getOracleData() external view override returns (OracleData memory
    oracleData) {
    ...
    (/* */, uint256 supplyCap) =
        IPoolDataProvider(POOL_DATA_PROVIDER).getReserveCaps(underlying);
    // Supply caps are returned as whole token values
    supplyCap = supplyCap * UNDERLYING_PRECISION;
    uint256 aTokenSupply =
        IPoolDataProvider(POOL_DATA_PROVIDER).getATokenTotalSupply(underlying);
    // If supply cap is zero, that means there is no cap on the pool
    if (supplyCap == 0) {
        oracleData.maxExternalDeposit = type(uint256).max;
    } else if (supplyCap <= aTokenSupply) {
        oracleData.maxExternalDeposit = 0;
    } else {
        // underflow checked as consequence of if / else statement
        oracleData.maxExternalDeposit = supplyCap - aTokenSupply;
    }
```
However, AAVE's restrictions are as follows: ValidationLogic.sol#L81-L88
```solidity
require(
    supplyCap == 0 ||
    ((IAToken(reserveCache.aTokenAddress).scaledTotalSupply() +
    uint256(reserve.accruedToTreasury)).rayMul(reserveCache.nextLiquidityIndex)
    + amount) <=
    supplyCap * (10 ** reserveCache.reserveConfiguration.getDecimals()),
    Errors.SUPPLY_CAP_EXCEEDED
);
```
The current implementation lacks subtraction of uint256(reserve.accruedToTreasury).rayMul(reserveCache.nextLiquidityIndex). An overly large maxExternalDeposit may cause rebalance() to be unable to execute.

## Recommendation
subtract uint256(reserve.accruedToTreasury)).rayMul(reserveCache.nextLiquidityIndex)
