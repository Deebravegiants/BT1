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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1352_
