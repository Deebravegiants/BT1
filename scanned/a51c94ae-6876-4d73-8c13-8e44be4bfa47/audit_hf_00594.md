# [H] H-02 | Liquidity Providers Can Abuse Unrealized Gains To Push Pool Utilization Over One Hundred

## Summary
Severity: High
Contest weight: 0.2508
Dataset id: 2092
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract’s AUM calculation logic incorrectly treats negative unrealized proﬁt and loss from
traders as an increase in the pool’s available collateral. This is because in the removeLiquidity
function the following check is performed.
However, if we take a look at the _aumUsd function, we can see that the upnl can be negative in case
that the traders are at a loss and owe value to the collateral pool.
In that case, _aumUsdWithoutPnl().toInt256() will be subtracted a negative number which will
artiﬁcially increase the ﬁnal aum allowing liquidity providers to remove more liquidity than is
genuinely available and, in some cases, even push the pool’s utilization above 100%.
When utilization surpasses 100% or is very high, the borrowing rate curve causes dramatically
increased costs for traders as it grows exponentially near full utilization, which severely
disadvantages traders who are forced to pay these escalated costs.

## Recommendation
Update the AUM computation to ensure that negative unrealized PnL owed by traders does not
inﬂate the pool's available collateral. Instead of allowing negative unrealized PnL to translate into a
higher AUM during the removal of liquidity, enforce a lower bound of zero on the upnl =
_traderTotalUpnlUsd(marketId) calculation or introduce a separate accounting mechanism to
distinguish between actual collateral and unrealized trader losses.
