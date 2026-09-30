# [M] Incorrect slippage protection in addLiquidityCurve and removeLiquidityCurve due to missing virtual price conversion

## Summary
Severity: Medium
Contest weight: 0.2366
Dataset id: 5473
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The addLiquidityCurve and removeLiquidityCurve functions contain incorrect slippage protection checks that compare LP token amounts directly with token values without accounting for the LP token's virtual price. In addLiquidityCurve, the function checks:
require(
    minLpAmount >= valueDeposited * maxSlippage / 1e18,
    "MainnetController/min-amount-not-met"
);
This is incorrect because minLpAmount represents LP tokens (shares of the pool), while valueDeposited represents the total value of the tokens that should be deposited into Curve. These values cannot be directly compared without converting the LP tokens to their underlying value using Curve's get_virtual_price() function. Similarly, in removeLiquidityCurve, the function checks:
require(
    valueMinWithdrawn >= lpBurnAmount * maxSlippage / 1e18,
    "MainnetController/min-amount-not-met"
);
Here, valueMinWithdrawn represents token values, while lpBurnAmount represents LP tokens. Again, these cannot be directly compared without accounting for the virtual price.
Impact: These errors currently have the following impact assuming the virtual price only increases starting from 1e18.
1. For addLiquidityCurve: The check is too strict. It will reject transactions with acceptable slippage levels because it's comparing LP tokens directly with token values. This is because after multiplying minLpAmount by the virtual price (which is > 1e18), the left side of the comparison would be greater, therefore making the check harder to satisfy than intended.
2. For removeLiquidityCurve: The check is too soft. It will allow transactions with excessive slippage to pass because it's comparing token values with LP tokens. This allows a lower valueMinWithdrawn to pass than should be permitted.

## Recommendation
For addLiquidityCurve, convert the LP tokens to their value equivalent:
require(
    minLpAmount * curvePool.get_virtual_price() / 1e18 >= valueDeposited * maxSlippage / 1e18,
    "MainnetController/min-amount-not-met"
);
For removeLiquidityCurve, the correct check would be:
require(
    valueMinWithdrawn >= lpBurnAmount * curvePool.get_virtual_price() * maxSlippage / 1e36,
    "MainnetController/min-amount-not-met"
);
