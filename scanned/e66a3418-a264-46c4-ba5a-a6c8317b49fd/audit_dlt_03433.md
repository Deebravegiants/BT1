# [M] Incorrect Return Value in `CompoundConnector.getBorrowBalanceInBase()` Affecting TVL Calculation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1352
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/tree/main/contracts/connectors/CompoundConnector.sol#L101-L102
https://github.com/code-423n4/2024-04-noya/tree/main/contracts/connectors/CompoundConnector.sol#L117-L120
https://github.com/code-423n4/2024-04-noya/tree/main/contracts/connectors/CompoundConnector.sol#L85-L89
https://github.com/code-423n4/2024-04-noya/tree/main/contracts/connectors/CompoundConnector.sol#L128-L130


# Vulnerability details

## Impact
The borrowed debt value is in wrong term, and the TVL calculation of Compound connector might revert or be inflated.

## Proof of Concept

`CompoundConnector.getCollBlanace()` correctly returns collateral values denominated in the the Comet's base token. The resulting collateral value is the sum of the principal and the user's collateral value. 

```solidity
CompoundConnector.sol
101:             uint256 principalInBase = uint256(uint104(userBasic.principal));
102:             CollValue += principalInBase;
```

The first one - principal is in correct terms of Comet's base token. The second one is `collateralValueInVirtualBase`. Within the calculation of `collateralValueInVirtualBase`, `collateralBalance * collateralPriceInVirtualBase / info.scale` is in terms of USD, and `(USD value) * baseScale / basePrice` is also in terms of Comet's base token. 

```solidity
CompoundConnector.sol
117:                 uint256 collateralValueInVirtualBase =
118:                     collateralBalance * collateralPriceInVirtualBase * baseScale / info.scale / basePrice;

120:                 else CollValue += collateralValueInVirtualBase;
```

But `CompoundConnector.getBorrowBalanceInBase()` returns the borrow balance in USD scale(same as liquidity). As we can see from the following code snippet, `borrowBalanceInBase` is in Comet's base token, and `(borrowBalanceInBase * basePriceInVirtualBase) / comet.baseScale()` is in USD.

```solidity
CompoundConnector.sol
85:         uint256 borrowBalanceInBase = comet.borrowBalanceOf(address(this));
86:         if (borrowBalanceInBase == 0) return 0;
87:         address basePriceFeed = comet.baseTokenPriceFeed();
88:         uint256 basePriceInVirtualBase = comet.getPrice(basePriceFeed);
89:         borrowBalanceInVirtualBase = (borrowBalanceInBase * basePriceInVirtualBase) / comet.baseScale();
```

When calculating the TVL from this Compound connector, the TVL balance is calculated by the subtraction of the borrowed debt from the collateral. The borrowed debt should be in the scale of the Comet's base token, but it is in USD because `getBorrowBalanceInBase()` returns USD instead of base token. 

```solidity
CompoundConnector.sol
128:         uint256 positiveBalance = getCollBlanace(IComet(market), false);
129:         uint256 negativeBalance = getBorrowBalanceInBase(IComet(market));
130:         uint256 balance = positiveBalance - negativeBalance;
```

The scale mismatch between the collateral value (denominated in the Comet's base token) and the borrowed debt value (denominated in USD) can lead to some issues in the protocol's functionality.

If the borrowed debt value returned by `getBorrowBalanceInBase()` is much greater than the correct value in the base token scale, the `_getPositionTVL()` function will revert, disrupting the overall functionality of the protocol.

Conversely, if the borrowed debt value is much smaller than the correct value in the base token scale, the borrowed debt will effectively be ignored in the TVL calculation. This will result in an inflated TVL.

## Tools Used
Manual Review

## Recommended Mitigation Steps
`getBorrowBalanceInBase()` could return `borrowBalanceInBase` which is in terms of the Comet's base token instead of calculation using the price of the base token.


## Assessed type

Error
