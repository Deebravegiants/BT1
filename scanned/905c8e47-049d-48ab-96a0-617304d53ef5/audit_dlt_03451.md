# [M] Improper price validation in CompoundConnector.sol will lead to stale prices being used.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1177
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L84-L90
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L115
https://github.com/compound-finance/comet/blob/b303912ded46f7feb00286964e733b31c6bc30f3/contracts/Comet.sol#L469-L477


# Vulnerability details

In CompoundConnector the functions 
* [getBorrowBalanceInBase()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L84-L90)
* [getCollBlanace()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L115)

both derive the value of an asset by getting the price feed and calling [comet.getPrice()](https://github.com/compound-finance/comet/blob/b303912ded46f7feb00286964e733b31c6bc30f3/contracts/Comet.sol#L469-L477) which returns the price of an asset which is further use to calculate the borrow and collateral balance of the connector.

[getBorrowBalanceInBase()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L84-L90)
```solidity
    function getBorrowBalanceInBase(IComet comet) public view returns (uint256 borrowBalanceInVirtualBase) {
        uint256 borrowBalanceInBase = comet.borrowBalanceOf(address(this));
        if (borrowBalanceInBase == 0) return 0;
@>      address basePriceFeed = comet.baseTokenPriceFeed();
@>      uint256 basePriceInVirtualBase = comet.getPrice(basePriceFeed);
        borrowBalanceInVirtualBase = (borrowBalanceInBase * basePriceInVirtualBase) / comet.baseScale();
    }
```

[getCollBlanace()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L115)

```solidity
    function getCollBlanace(IComet comet, bool riskAdjusted) public view returns (uint256 CollValue) {
        IComet.UserBasic memory userBasic = comet.userBasic(address(this));
        uint16 assetsIn = userBasic.assetsIn;
        uint256 basePrice = comet.getPrice(comet.baseTokenPriceFeed());
        uint256 baseScale = comet.baseScale();
        if (userBasic.principal > 0) {
            uint256 principalInBase = uint256(uint104(userBasic.principal));
            CollValue += principalInBase;
        }
        uint8 numberOfAssets = comet.numAssets();


        // Iterate through assets, and determine the risk adjusted collateral value.
        for (uint8 i; i < numberOfAssets; ++i) {
            if (isInAsset(assetsIn, i)) {
                IComet.AssetInfo memory info = comet.getAssetInfo(i);


                // Check if we have a collateral balance.
                (uint256 collateralBalance,) = comet.userCollateral(address(this), info.asset);


                // Get the value of collateral in virtual base.
@>              uint256 collateralPriceInVirtualBase = comet.getPrice(info.priceFeed);


                uint256 collateralValueInVirtualBase =
                    collateralBalance * collateralPriceInVirtualBase * baseScale / info.scale / basePrice;
                if (riskAdjusted) CollValue += collateralValueInVirtualBase * info.liquidateCollateralFactor / 1e18;
                else CollValue += collateralValueInVirtualBase;
            } // else user collateral is zero.
        }
    }
```
The `issue` here is that the function [getPrice()](https://github.com/compound-finance/comet/blob/b303912ded46f7feb00286964e733b31c6bc30f3/contracts/Comet.sol#L469-L477) which these functions use from `comet` does not sufficiently validate the price returned from chainlink's `latestRoundData()` as it only ensures that the price returned is a positive non-zero number but does `not` check for staleness of the feed. During feed staleness, the value returned is > 0 (passing the check) but will remain the `same` even if the actual price has altered leading to incorrect prices being returned.
```solidity
     * @notice Get the current price from a feed
     * @param priceFeed The address of a price feed
     * @return The price, scaled by `PRICE_SCALE`
     */
    function getPrice(address priceFeed) override public view returns (uint256) {
        (, int price, , , ) = IPriceFeed(priceFeed).latestRoundData();
 @>     if (price <= 0) revert BadPrice(); //@audit should also validate updatedat to avoid staleness
        return uint256(price);
    }
```



## Impact
The use of `stale` prices will lead to incorrect value calculations, and these affected functions are used to derive the positions TVL which will result in accounting issues in the protocol.

## Tools Used
Manual Review

## Recommended Mitigation Steps
The affected functions [getBorrowBalanceInBase()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L84-L90) and [getCollBlanace()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L115) should be changed to use `ChainlinkOracleConnector::getValueFromChainlinkFeed()` for value calculations as it properly validates the price returned for staleness. The price feed address returned from `comet` should be inputted as `AggregatorV3Interface(address) in the chainlink oracle function.


## Assessed type

Oracle
