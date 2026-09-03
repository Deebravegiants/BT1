# [H] [Tomo-H1] Can withdraw all funds in the DODORouteProxy contract

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/67
Type: sherlock-finding

## Details
Tomo

high

# [Tomo-H1] Can withdraw all funds in the DODORouteProxy contract

## Summary

Can withdraw all funds in the DODORouteProxy contract

## Vulnerability Detail
If the following conditions are passed in `dodoMultiSwap()`, the transaction will succeed.


1. `minReturnAmount` > 0 in `dodoMultiSwap()`
2. `assetFrom.length == splitNumber.length` in `dodoMultiSwap()`
3. The balance of `toToken` in this contract is greater than before executing `multiSwap()` in `dodoMultiSwap()`
4. `receiveAmount >= minReturnAmount` in `_routeWithdraw()`

### Example
Assume the balance of WETH = 10*8*18 USDC, WBTC = 10*10*8

1. Eve executes the `dodoMultiSwap()` as the following parameters contain
`midToken = [ETH, WBTC, ETH]`,`minReturnAmount = 1`, `assetFrom = [address(this), address(this),address(this)]`
2. Assume the value of `toTokenOriginBalance` is 10*8*18 USDC
3. Eve deposits 1 wei USDC by using  `_deposit()` to the DODORouteProxy contract
4. As you can see, there are no check in the `multiSwap()` parameters.
5. Also, the only state variables used in this function are `curTotalAmount` and `totalWeight`. Other values depend on user input.
6. Users can set the values as follows by using `abi.decode()`
- `curPoolInfo.direction` = 0
- `curPoolInfo.poolEdition` = 1
- `curPoolInfo.weight` = 100
- `curPoolInfo.adapter` = address(EveAdapter)

The EveAdapter contract is like this.
[https://gist.github.com/Tomosuke0930/09a6b31cdaacd8ffa5ae40c6b6f089ee](https://gist.github.com/Tomosuke0930/09a6b31cdaacd8ffa5ae40c6b6f089ee)

7. And then, the all WBTC token in this contract transfer to `curPoolInfo.adapter` like this.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/67_
