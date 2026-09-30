# [H] In updateAToken and updateVariableDebtToken of the LendingPoolConfigurator encodedCall is constructed incorrectly

## Summary
Severity: High
Contest weight: 0.5547
Dataset id: 6607
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In updateAToken and updateVariableDebtToken of the LendingPoolConfigurator encodedCall is constructed incorrectly:
```solidity
bytes memory encodedCall = abi.encodeWithSelector(
    /*...*/ selector,
    cachedPool,
    // ...
    input.asset,
    input.incentivesController,
    decimals, // <--- `reserveType` is missing after here
    input.name,
    input.symbol,
    input.params
);
```
and thus RESERVE_TYPE, name, symbol and params will be set incorrectly in the proxy contracts. This will cause all the following calls to query or update data for a wrong reserve in the lending pool: pool.function(_underlyingAsset, RESERVE_TYPE, /*...*/ )

## Recommendation
Add the missing reserveType parameter and also make sure to instead of abi.encodeWithSelector use abi.encodeCall to avoid potential future mistakes regarding typos and incorrect parameter types.
