# [M] LP-4 | utilizationRate May Exceed Max Value

## Summary
Severity: Medium
Contest weight: 0.0885
Dataset id: 103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for the utilizationRatio to exceed the maxUtilization, as the premium value of traded options and the liquidity in hedged positions changes over time. In this scenario the utilizationRatio function will return a ratio greater than the maxUtilization, perturbing the interest rate calculations in the interestRate function.

## Recommendation
Return the interestRateParams.MaxUtilization if the utilizationRatio exceeds it. // (utilized collateral + MM + money on gmx) / NAV + if(ConvertDecimals.convertTo18(ConvertDecimals.convertFrom18AndRoundUp + (_utilizedCollateral + MM + hedgerTotalLiq, _decimals) + .mulDivUp( + 10 ** _decimals, NAV_Priced), _decimals) >= interestRateParams.MaxUtilization) + return interestRateParams.MaxUtilization return ConvertDecimals.convertTo18( ConvertDecimals.convertFrom18AndRoundUp(_utilizedCollateral + MM + hedgerTotalLiq, _decimals).mulDivUp( 10 ** _decimals, NAV_Priced ), _decimals );
