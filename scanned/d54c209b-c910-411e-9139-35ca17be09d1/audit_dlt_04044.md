# [M] Missing zero approval

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/109
Type: sherlock-finding

## Details
csanuragjain

medium

# Missing zero approval

## Summary
Few tokens require the approval limit to be 0 before setting a new approval limit like USDT. If trade.sellToken is one of such tokens then the approval will fail causing the trade to fail

## Vulnerability Detail
1. Trade is executed using [_executeInternal function](https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/trading/TradingUtils.sol#L29)

```python
function _executeInternal(
        Trade memory trade,
        uint16 dexId,
        address spender,
        address target,
        uint256 msgValue,
        bytes memory executionData
    ) internal returns (uint256 amountSold, uint256 amountBought) {
...
if (spender != Deployments.ETH_ADDRESS && DexId(dexId) != DexId.NOTIONAL_VAULT) {
            _approve(trade, spender);
        }
...
}
```

2. Now _approve function is called

```python
function _approve(Trade memory trade, address spender) private {
        uint256 allowance = _isExactIn(trade) ? trade.amount : trade.limit;
        IERC20(trade.sellToken).checkApprove(spender, allowance);
    }
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/109_
