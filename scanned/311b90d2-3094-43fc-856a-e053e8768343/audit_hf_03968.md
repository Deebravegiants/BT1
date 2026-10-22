# [M] Invalid oracle version can cause the vault to

## Summary
Severity: Medium
Contest weight: 0.6915
Dataset id: 20331
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
StrategyLib._loadContext for the market loads currentPosition as:
```solidity
context.currentPosition = registration.market.pendingPosition(global.currentId);
```
However, this is unadjusted position, so its value is incorrect if invalid oracle version happens while this position is pending. Later on, when calculating minimum and maximum positions enforced by the vault in the market, they're calculated in _positionLimit:
```solidity
function _positionLimit(MarketContext memory context) private pure returns (
    return (
        // minimum position size before crossing the net position
        context.currentAccountPosition.maker.sub(
            context.currentPosition.maker
            .sub(context.currentPosition.net().min(context.currentPosition.maker))
            .min(context.currentAccountPosition.maker)
            .min(context.closable)
        ),
        // maximum position size before crossing the maker limit
        context.currentAccountPosition.maker.add(
            context.riskParameter.makerLimit
            .sub(context.currentPosition.maker.min(context.riskParameter.makerLimit))
        )
    );
}
```
And the target maker size for the market is set in allocate:
```solidity
(targets[marketId].collateral, targets[marketId].position) = (
    _locals.marketAssets
    .muldiv(registrations[marketId].leverage, contexts[marketId].latestPrice.abs())
    .min(_locals.maxPosition)
    .max(_locals.minPosition)
);
```
Since context.currentPosition is incorrect, it can happen that both _locals.minPosition and _locals.maxPosition are too high, the vault will open too large and risky position, breaking its risk limit and possibly getting liquidated, especially if it happens during high volatility. If invalid oracle version happens, the vault might open too large and risky position in such market, potentially getting liquidated and vault users losing funds due to this liquidation. StrategyLib._loadContext loads current global position without adjusting it, meaning context.currentPosition is incorrect if invalid oracle version happens: ages/perennial-vault/contracts/lib/StrategyLib.sol#L131 This leads to incorrect position limit calculations: ages/perennial-vault/contracts/lib/StrategyLib.sol#L172-L187 This, in turn, leads to incorrect target vault's position calculation for the market: ages/perennial-vault/contracts/lib/StrategyLib.sol#L93-L99

## Recommendation
Adjust global current position after loading it:
```solidity
context.currentPosition = registration.market.pendingPosition(global.currentId);
context.currentPosition.adjust(registration.market.position());
```
