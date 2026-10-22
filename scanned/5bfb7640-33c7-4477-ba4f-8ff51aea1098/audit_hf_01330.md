# [M] Rounding directions

## Summary
Severity: Medium
Contest weight: 0.5444
Dataset id: 6612
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• GenericLogic.sol#L236-L242, MiniPoolGenericLogic.sol#L202-L209: Make sure all operations round-up when calculating totalDebtInETH.
• AToken.sol#L184-L185: Best to round-up amountScaled.
• ValidationLogic.sol#L205-L212, MiniPoolValidationLogic.sol#L208-L214: It would be best to round up the vars.amountOfCollateralNeededETH or instead check:
```solidity
vars.userBorrowBalanceETH + validateParams.amountInETH <= (vars.userCollateralBalanceETH).percentMul(vars.currentLtv)
```

## Recommendation
• GenericLogic.sol#L236-L242, MiniPoolGenericLogic.sol#L202-L209: Make sure all operations round-up when calculating totalDebtInETH.
• AToken.sol#L184-L185: Best to round-up amountScaled.
• ValidationLogic.sol#L205-L212, MiniPoolValidationLogic.sol#L208-L214: It would be best to round up the vars.amountOfCollateralNeededETH or instead check:
```solidity
vars.userBorrowBalanceETH + validateParams.amountInETH <= (vars.userCollateralBalanceETH).percentMul(vars.currentLtv)
```
