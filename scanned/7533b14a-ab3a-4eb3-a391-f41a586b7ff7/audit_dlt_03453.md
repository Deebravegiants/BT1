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
        _updateTokenInRegistry(collateralType);
>       _updateTokenInRegistry(usdToken);
    }

    function _getPositionTVL(HoldingPI memory p, address base) public view override returns (uint256 tvl) {
        (uint128 accountId, address collateralType) = abi.decode(p.data, (uint128, address));
        (uint256 totalDeposited, uint256 totalAssigned, uint256 totalLocked) =
            SNXCoreProxy.getAccountCollateral(accountId, collateralType);
>       tvl = _getValue(collateralType, base, totalDeposited + totalAssigned);
    }
```

We can find the implementation of `getAccountCollateral` here: https://github.com/Synthetixio/synthetix-v3/blob/main/protocol/synthetix/contracts/storage/Account.sol#L101-L116

```solidity
    function getCollateralTotals(
        Data storage self,
        address collateralType
    )
        internal
        view
        returns (uint256 totalDepositedD18, uint256 totalAssignedD18, uint256 totalLockedD18)
    {
        totalAssignedD18 = getAssignedCollateral(self, collateralType);
>       totalDepositedD18 =
>           totalAssignedD18 +
>           self.collaterals[collateralType].amountAvailableForDelegationD18;
        totalLockedD18 = self.collaterals[collateralType].getTotalLocked();

        return (totalDepositedD18, totalAssignedD18, totalLockedD18);
    }
```

## Proof of Concept

N/A

## Tools Used

Manual review.

## Recommended Mitigation Steps

The collateral calculation can just use `totalDeposited`.

However the debt calculation is a bit tricky. The closest API for fetching debt is using `updateAccountDebt` https://github.com/Synthetixio/synthetix-v3/blob/main/protocol/synthetix/contracts/storage/Pool.sol#L366-L373, but it is not a view function. Not really sure what the best solution here is.



## Assessed type

Other
