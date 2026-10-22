# [H] H-1 An inﬂated fee in the AMM leads to a partial AMM DOS

## Summary
Severity: High
Contest weight: 0.3303
Dataset id: 7105
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The adminfeesx variable is not divided by BORROWED_PRECISION in AMM withdraw():
If withdrawal is the last one - transfer dust to admin fees
if new_shares == 0:
if x > 0:
self.adminfeesx += x
if y > 0:
self.adminfeesy += unsafediv(y, COLLATERALPRECISION)
AMM.vy#L794
If borrowed_token is WBTC (decimals=8), then the error in fee accrual will be on the order of 10 magnitudes. A hacker could perform an inﬂation attack on the nearest available tick to trigger this piece of code and inﬂate adminfeesx to the total amount of the borrowed_token balance in the AMM, while losing 10 magnitudes less funds than the ﬁnal inﬂation amount. If the hacker then calls collect_fees(), which is a public method, all borrowed tokens from the AMM will be sent to FACTORY.fee_receiver(). This will lead to a partial DOS of the AMM, as users will lose the ability to withdraw borrowed tokens from ticks, as there simply won't be any funds in the AMM for this.
There are a few notes on this:
1. This attack does not depend on ADMIN_FEE; the code is always activated when there is dust in the tick. In order to execute the attack, the hacker needs to inﬂate the share price in the tick, causing the dust to have a large value.
2. AMM uses dead shares, but price inﬂation is still possible via the exchange() method or other means. It's just not proﬁtable for the hacker.
3. Currently, collectfees() reverts as Vault does not have a feereceiver() method which is called by the collectfees() method. Still, if the collectfees() revert issue is addressed by introducing a fee_receiver() in the factory, then the fee inﬂation bug will arise.

## Recommendation
We recommend adding the missing division by the BORROWED_PRECISION:
self.adminfeesx += unsafediv(x, BORROWEDPRECISION)
