# [M] maintainer can be pushed out

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-03
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/5
Type: code-finding

## Details
# Email address

mail@gpersoon.com


# Handle

gpersoon


# Eth address

gpersoon.eth


# Vulnerability details

The function liquidate (in both CrossMarginLiquidation.sol and IsolatedMarginLiquidation.sol) can be called by everyone.
If an attacker calls this repeatedly then the maintainer will be punished and eventually be reported as maintainerIsFailing
And then the attacker can take the payouts


# Proof of concept

When a non authorized address repeatedly calls liquidate then the following happens:
isAuthorized = false
which means maintenanceFailures[currentMaintainer] increases
after sufficient calls it will be higher than the threshold and then
maintainerIsFailing() will be true
This results in canTakeNow being true
which finally means the following will be executed:
   Fund(fund()).withdraw(PriceAware.peg, msg.sender, maintainerCut);


# Impact

An attacker can push out a maintainer and take over the liquidation revenues


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-04-marginswap-findings/issues/5_
