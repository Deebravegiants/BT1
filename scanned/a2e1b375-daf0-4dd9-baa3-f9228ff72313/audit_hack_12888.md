# [M] Vault: Liquidation does not reward MEV liquidator

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373
Type: audit-issue

## Details
# Vault: Liquidation does not reward MEV liquidator

## Summary

MEV searchers should be rewarded with liquidation reward fee. But the implementation does not reward liquidator.

## Vulnerability Detail

From the [documentation](https://docs.unstoppable.ooo/unstoppable/products/unstoppable-dex/liquidations#layer-3-mev-searchers):

```markdown
The liquidation opportunity is exposed on-chain for MEV bots. (This is how liquidations on AAVE and Euler work for example).

These bots are constantly scanning for profitable opportunities, and the liquidation fee reward is one of them.
```

There are two cases in the implemenation.

1. For a bad debt liquidation where `amount_out_received <= debt_amount`, no reward is distributed.
2. For a 'good debt' liquidation where `amount_out_received > debt_amount`, reward is distributed to LP and protocol by _distribute_trading_fee.

```solidity
    if amount_out_received > debt_amount:
        # margin left
        remaining_margin: uint256 = amount_out_received - debt_amount
        penalty = min(penalty, remaining_margin)
        self.margin[position.account][position.debt_token] -= penalty
        self._distribute_trading_fee(position.debt_token, penalty)

    log PositionLiquidated(position.account, _position_uid, position)
# end of function
```

There is no reward for liquidator.

## Impact

The liquidation will not be assisted by MEV searchers which could increase bad debt rate.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373

## Tool used

Manual Review

## Recommendation

Distribute liquidation reward to liquidator.
