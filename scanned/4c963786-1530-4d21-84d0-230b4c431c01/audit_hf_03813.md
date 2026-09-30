# [M] Calc.boundedAdd used intitally but later reg-

## Summary
Severity: Medium
Contest weight: 0.1654
Dataset id: 20035
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MarketDecrease order flow the funding amount per size calculation uses Calc.boundedAdd but further down the call path there is a calculation that does not use Calc.boundedSubtract but rather a regular -, which could cause overflow errors. In MarketUtils.getNextFundingAmountPerSize the funding amount per size variables in the GetNextFundingAmountPerSizeResult variable are calculated using Calc.boundedAdd(a,b). If the inputs to the function are (type(int256).min+10,-12), for example, then the value returned will be type(int256).min i.e. it will not cause an arithmetic overflow, like it would if the values were just added normally with +. Further down the call path of MarketDecrease in MarketUtils.getFundingFeeAmount the funding amount is negated, and negating type(int256).min results in an arithmetic overflow. If the point of defending overflow of the funding amount per size variables was to allow execution to pass without failure then all calculations involving the funding amount per size variables should use Calc.boundedAdd or Calc.boundedSub. MarketDecrease orders that would be expected to pass would fail, causing them to be cancelled.

## Recommendation
Use Calc.boundedAdd & Calc.boundedSub on all calculations involving addition and subtraction with funding amount per size variables.
