# [H] `SNXConnector.sol` TVL calculation is incorrect.

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1120
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/SNXConnector.sol#L121-L126


# Vulnerability details

## Impact

The TVL calculation for `SNXConnector.sol` is incorrect.

## Bug Description

SNXConnector allows depositing collateral and minting SUSD. 

There are two issues for TVL calculation code:

1. It does not account for the debt occurred for minting SUSD
2. `totalDeposited` already includes `totalAssigned`

Note that the minted SUSD tokens are already calculated into TVL by calling `_updateTokenInRegistry(usdToken);` while minting SUSD, so the debt part must be calculated as well.

```solidity
    function mintOrBurnSUSD(
        uint256 _amount,
        uint128 _accountId,
        uint128 poolId,
        address collateralType,
        bool mintOrBurn
    ) public onlyManager {
        // Mint or burn
        address usdToken = SNXCoreProxy.getUsdToken();
        if (mintOrBurn) {
            SNXCoreProxy.mintUsd(_accountId, poolId, collateralType, _amount);
        } else {
            _approveOperations(usdToken, address(SNXCoreProxy), _amount);
            SNXCoreProxy.burnUsd(_accountId, poolId, collateralType, _amount);
        }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1120_
