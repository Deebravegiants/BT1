# [M] Withdraw auction could process an unchecked order if toPull value is 0

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/97
Type: sherlock-finding

## Details
caventa

medium

# Withdraw auction could process an unchecked order if toPull value is 0

## Summary
Withdraw auction could process an unchecked order if toPull value is 0

## Vulnerability Detail
The following for-loop will not be executed if toPull value is 0

```solidity
uint256 sqthRequired = ICrabStrategyV2(crab).getWsqueethFromCrabAmount(_p.crabToWithdraw);
uint256 toPull = sqthRequired;
for (uint256 i = 0; i < _p.orders.length && toPull > 0; i++) {
    _checkOrder(_p.orders[i]);
    require(!_p.orders[i].isBuying, "auction order is not selling");
    require(_p.orders[i].price <= _p.clearingPrice, "sell order price greater than clearing");
    if (_p.orders[i].quantity < toPull) {
        toPull -= _p.orders[i].quantity;
        IERC20(sqth).transferFrom(_p.orders[i].trader, address(this), _p.orders[i].quantity);
    } else {
        IERC20(sqth).transferFrom(_p.orders[i].trader, address(this), toPull);
        toPull = 0;
    }
}
```

 and the order will not be checked as this line of code will not be executed
 
```solidity
_checkOrder(_p.orders[i]);
 ```
 
 Therefore, the remaining withdrawAuction code process the order which is  not checked

## Impact

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/97_
