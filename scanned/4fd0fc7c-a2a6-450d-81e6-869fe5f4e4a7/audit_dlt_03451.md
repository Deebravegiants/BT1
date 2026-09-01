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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1177_
