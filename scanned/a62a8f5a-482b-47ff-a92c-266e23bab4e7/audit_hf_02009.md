# [H] Incorrect `AutoDeleverageFactor`.

## Summary
Severity: High
Contest weight: 0.7945
Dataset id: 11387
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculation of AutoDeleverageFactor is incorrect.

https://github.com/Cyfrin/2025-01-zaros-part-2/blob/main/src/market-making/leaves/Market.sol#L174
```solidity
    function getAutoDeleverageFactor(
        ...
    )   ...
    {   ...
        UD60x18 unscaledDeleverageFactor = Math.min(marketDebtRatio, autoDeleverageEndThresholdX18).sub(
            autoDeleverageStartThresholdX18
        ).div(autoDeleverageEndThresholdX18.sub(autoDeleverageStartThresholdX18));

        // finally, raise to the power scale
        autoDeleverageFactorX18 = unscaledDeleverageFactor.pow(autoDeleverageExponentZX18);
    }
```

As we can see, when marketRatio >= ADL start threshold, the smaller debt, the smaller autoDeleverageFactor.
For example:
When marketDebtRatio = autoDeleverageStartThresholdX18, the calcuatated AutoDeleverageFactor is zero.
When marketDebtRatio = autoDeleverageEndThresholdX18, the calcuatated AutoDeleverageFactor is one.

https://github.com/Cyfrin/2025-01-zaros-part-2/blob/main/src/market-making/branches/CreditDelegationBranch.sol#L159
```solidity    
    function getAdjustedProfitForMarketId(
        ...
        if (market.isAutoDeleverageTriggered(delegatedCreditUsdX18, marketTotalDebtUsdX18)) {
            // if the market's auto deleverage system is triggered, it assumes marketTotalDebtUsdX18 > 0
            adjustedProfitUsdX18 =
            market.getAutoDeleverageFactor(delegatedCreditUsdX18, marketTotalDebtUsdX18).mul(adjustedProfitUsdX18);
        }
```

https://github.com/Cyfrin/2025-01-zaros-part-2/blob/main/src/perpetuals/branches/SettlementBranch.sol#L499
```solidity
        if (ctx.pnlUsdX18.gt(SD59x18_ZERO)) {
            IMarketMakingEngine marketMakingEngine = IMarketMakingEngine(perpsEngineConfiguration.marketMakingEngine);

            ctx.marginToAddX18 =
            marketMakingEngine.getAdjustedProfitForMarketId(marketId, ctx.pnlUsdX18.intoUD60x18().intoUint256());

            tradingAccount.deposit(perpsEngineConfiguration.usdToken, ctx.marginToAddX18);

            // mint settlement tokens credited to trader; tokens are minted to
            // address(this) since they have been credited to the trader's margin
            marketMakingEngine.withdrawUsdTokenFromMarket(marketId, ctx.marginToAddX18.intoUint256());
        }
```

As a result, Traders receive their full pnls when marketDebtRatio = autoDeleverageEndThresholdX18, but none when marketDebtRatio = autoDeleverageStartThresholdX18.

Traders do not receive their PnLs at all when the state enters the ADL state.

## Recommendation
https://github.com/Cyfrin/2025-01-zaros-part-2/blob/main/src/market-making/leaves/Market.sol#L174
```diff
    function getAutoDeleverageFactor(
        ...
    )   ...
    {   ...
        UD60x18 unscaledDeleverageFactor = Math.min(marketDebtRatio, autoDeleverageEndThresholdX18).sub(
            autoDeleverageStartThresholdX18
        ).div(autoDeleverageEndThresholdX18.sub(autoDeleverageStartThresholdX18));

        // finally, raise to the power scale
-       autoDeleverageFactorX18 = unscaledDeleverageFactor.pow(autoDeleverageExponentZX18);
+       autoDeleverageFactorX18 = UD60x18_UNIT.sub(unscaledDeleverageFactor).pow(autoDeleverageExponentZX18);
    }
```
