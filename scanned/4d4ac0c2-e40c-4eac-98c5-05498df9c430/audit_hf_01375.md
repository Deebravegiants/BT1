# [H] H-1 Addresses for oracles should be whitelisted

## Summary
Severity: High
Contest weight: 0.3274
Dataset id: 7066
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the Pools Factory allows users to create pools with user-supplied oracles to determine prices of assets:
CurveStableSwapFactoryNG.vy#L531
CurveStableSwapFactoryNG.vy#L657
This allows malicious users to create pools with oracles that can change their returned values. This could lead to imbalanced pools where a malicious user can steal assets via swaps or liquidity removes. However, the pools created by malicious users should not accumulate any liquidity since these pools will not be accepted by the community and LPs in these pools will not be rewarded with CRV tokens.
But there is one more dangerous scenario that can lead to lost value by Curve users. Let's imagine a situation where a new protocol builds an integration with Curve and deploys a stable pool with some custom mechanics, which is allowed because of the user-supplied oracles. But developers didn't pay enough attention to the security of their price oracle, and a hack took place with the manipulation of the price oracle (flashloan manipulation, donation attack, price control in the pool, etc.) set by that team in the pool. In this case, Curve LPs will lose value.
In our opinion, it is impossible to control the quality of price oracles in an automated way (it is impossible to build this type of check inside any function) which is why we recommend adding a whitelist for oracles so the community can assess the quality of new oracles. Moreover, pools with volatile oracles will lead to permanent losses for LPs (if someone decides to create a wETH/wBTC pool with an oracle that sets the price from wETH to wBTC).

## Recommendation
We recommend adding a whitelist for oracles' addresses.
