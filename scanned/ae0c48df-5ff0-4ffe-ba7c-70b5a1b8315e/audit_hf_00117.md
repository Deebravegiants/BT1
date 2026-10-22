# [M] maintainer can be pushed out

## Summary
Severity: Medium
Contest weight: 0.1761
Dataset id: 254
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function liquidate (in both `CrossMarginLiquidation.sol` and `IsolatedMarginLiquidation.sol`) can be called by everyone. If an attacker calls this repeatedly then the maintainer will be punished and eventually be reported as maintainerIsFailing. And then the attacker can take the payouts.

When a non authorized address repeatedly calls liquidate then the following happens: `isAuthorized = false` which means `maintenanceFailures[currentMaintainer]` increases. After sufficient calls it will be higher than the threshold and then `maintainerIsFailing()` will be true. This results in `canTakeNow` being true, which finally means the following will be executed:

`Fund(fund()).withdraw(PriceAware.peg, msg.sender, maintainerCut);`

An attacker can push out a maintainer and take over the liquidation revenues.

Recommend put authorization on who can call the liquidate function, review the maintainer punishment scheme.

I believe this issue is not a vulnerability, due to the checks in lines 326-335. Even if someone comes in first and claims the maintainer is failing they can do their job in the same or next block and get all / most of their failure record extinguished.

Acknowledging feedback from @werg, but maintaining the reported risk level of `medium` since this has implications on token logic.

## Recommendation
No recommendation
