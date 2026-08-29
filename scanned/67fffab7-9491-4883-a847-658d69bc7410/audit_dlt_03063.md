# [M] Burning FlashFee breaks a core protocol invariant

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1276
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/USDO.sol#L102


# Vulnerability details

Most CDP systems have a key invariant:
SUM(DEBT) = Total Supply

This ensures that if all debt is repaid, the total supply goes to zero

That's because there's an implicit invariant, that if every debtor were to repay, since the system is overcollateralized, there would be no tokens left.

However, `flashLoan` takes the fee and `burn`s it.

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/USDO.sol#L102

```solidity
     _burn(address(receiver), amount + fee);
```

This means that some `debt` will remain registered in the system, but will not have the corresponding USD0 to repay it

The paradoxical conclusion to this, is a scenario in which a person opens a CDP, borrows X tokens, then burns them via flashloanFees and they won't be able to ever repay, nor anybody would be able to liquidate them and close their position.

### POC
- Mint some USD0
- Flashloan for any use
- Pay the fee
- You can no longer close your own position

While someone is always likely to keep their CDP open, the design creates a scenario where if sufficient people are taking on high leverage, there may be insufficient tokens to allow them to repay and to liquidate them.

### Mitigation

Instead of burning the fee, either distribute it to Stakers or to the DAO


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1276_
